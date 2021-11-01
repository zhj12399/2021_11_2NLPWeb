from django.http import HttpResponseRedirect
from django.shortcuts import render
import pynlpir
import os
from NLPWebApp.models import Record
from datetime import datetime


# Create your views here.
def Submit(request):
    if request.method == "POST":
        # 获取用户输入的信息
        zh_raw_text = request.POST.get("zh_text_name")
        en_raw_text = request.POST.get("en_text_name")

        zh_raw_text = " ".join(zh_raw_text.splitlines())
        en_raw_text = " ".join(en_raw_text.splitlines())

        # 分词处理
        pynlpir.open()
        zh_pri_list = pynlpir.segment(zh_raw_text, pos_tagging=False)
        pynlpir.close()
        zh_pri_text = ''
        for item in zh_pri_list:
            zh_pri_text += item + " "

        zh_pri_text += '\n'
        en_raw_text += '\n'
        # 将输入的文件写入text，0为zh_raw，1为en_raw，2为zh_pri
        with open('raw.txt', 'w+', encoding='utf-8') as f:
            f.write(zh_raw_text + '\n')
            f.write(en_raw_text)
            f.write(zh_pri_text)

        now_time = datetime.now()
        Record.objects.create(time=now_time, chinese=zh_raw_text, english=en_raw_text, chinese_pri=zh_pri_text,
                              answer="post")

        # 将其他训练文本读进来
        with open("cnfile.txt", "r", encoding="utf-8") as f:
            for line in f:
                zh_pri_text += line
        with open("enfile.txt", "r", encoding="utf-8") as f:
            for line in f:
                en_raw_text += line

        # 将文件写入
        with open("zh.txt", 'w+', encoding="utf-8") as f:
            f.write(zh_pri_text)
        with open("en.txt", 'w+', encoding="utf-8") as f:
            f.write(en_raw_text)

        return HttpResponseRedirect('calculating/')
    else:
        return render(request, "home.html")


def calculating(request):
    if request.method == "POST":
        # 开始执行对其
        os.system('./plain2snt.out zh.txt en.txt')

        # 生成共现文件
        os.system('./snt2cooc.out zh.vcb en.vcb zh_en.snt > zh_en.cooc')
        os.system('./snt2cooc.out en.vcb zh.vcb en_zh.snt > en_zh.cooc')

        # 生成词类
        # os.system('./mkcls -pzh.txt -Vzh.vcb.classes opt')
        # os.system('./mkcls -pen.txt -Ven.vcb.classes opt')

        # GIZA++
        os.system('./GIZA++ -S zh.vcb -T en.vcb -C zh_en.snt -CoocurrenceFile zh_en.cooc -o z2e -OutputPath z2e')
        os.system('./GIZA++ -S en.vcb -T zh.vcb -C en_zh.snt -CoocurrenceFile en_zh.cooc -o e2z -OutputPath e2z')

        # 只提取第一个数据源
        os.system('python2 align_sym.py ./e2z/e2z.A3.final ./z2e/z2e.A3.final > aligned.grow-diag-final-and')

        ans_show = ''
        with open('aligned.grow-diag-final-and', 'r') as f:
            for line in f:
                ans_show += line

        os.system('python3 align_plot.py en.txt zh.txt aligned.grow-diag-final-and 0')

        return HttpResponseRedirect('../answering/')
    else:
        input_text_one = ""
        input_text_two = ""
        input_text_thr = ""
        with open('raw.txt', 'r', encoding='utf-8') as f:
            input_text_one += "输入的中文：" + f.readline()
            input_text_two += "输入的英文：" + f.readline()
            input_text_thr += "分割的中文：" + f.readline()
        return render(request, "calculating.html",
                      {"text_one": input_text_one, "text_two": input_text_two, "text_thr": input_text_thr})


def ans(request):
    if request.method == "POST":
        return HttpResponseRedirect('../')
    else:
        input_text_one = ""
        input_text_two = ""
        input_text_thr = ""
        with open('raw.txt', 'r', encoding='utf-8') as f:
            input_text_one += f.readline()
            input_text_two += f.readline()
            input_text_thr += f.readline()

        ans_text = ''
        with open('aligned.grow-diag-final-and', 'r', encoding='utf-8') as f:
            ans_text = f.readline()

        now_time = datetime.now()
        Record.objects.create(time=now_time, chinese=input_text_one, english=input_text_two, chinese_pri=input_text_thr,
                              answer=ans_text)
        input_text_one = "输入的中文：" + input_text_one
        input_text_two = "输入的英文：" + input_text_two
        input_text_thr = "分割的中文：" + input_text_thr
        ans_text = '分词结果：' + ans_text

        return render(request, "answering.html",
                      {"text_one": input_text_one, "text_two": input_text_two, "text_thr": input_text_thr,
                       "text_ans": ans_text})
