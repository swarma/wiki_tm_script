import sys
import re
import requests
import json

from time import sleep
from nltk.tokenize import sent_tokenize


def translate(source, direction):
    url = "http://api.interpreter.caiyunai.com/v1/translator"
    
    #WARNING, this token is a test token for new developers, and it should be replaced by your token
    token = "3975l6lr5pcbvidl6jl2"
    
    payload = {
            "source" : source, 
            "trans_type" : direction,
            "request_id" : "demo",
            "detect": True,
            }
    
    headers = {
            'content-type': "application/json",
            'x-authorization': "token " + token,
    }
    
    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    if not response.ok:
        count = 0
        while True:
            print("In processing : ", source[0])
            print(response.json())
            sleep(15)
            response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
            if response.ok:
                break
            else:
                count += 1

            if count >= 5:
                return ""

    return json.loads(response.text)['target']


def translate_passage(paragraphs, direction):
    batch = []
    recovered_evidence = []

    for i, p in enumerate(paragraphs):
        if not p.strip():
            continue

        sents = sent_tokenize(p)
        batch.extend(sents)
        evidence = [i] * len(sents)
        recovered_evidence.extend(evidence)

    trans_sents = translate(batch, direction)
    assert(len(trans_sents) == len(recovered_evidence))

    one_para = trans_sents[0]
    recovered_papras = []
    for j in range(recovered_evidence[0] - 0):
        recovered_papras.append("")

    for i in range(1, len(trans_sents)):
        if recovered_evidence[i-1] == recovered_evidence[i]:
            one_para += trans_sents[i]
        else:
            recovered_papras.append(one_para)
            for j in range(recovered_evidence[i] - recovered_evidence[i-1] - 1):
                recovered_papras.append("")
            one_para = trans_sents[i]

    recovered_papras.append(one_para)

    if len(recovered_papras) < len(paragraphs):
        comp = (len(paragraphs) - len(recovered_papras)) * [""]
        recovered_papras.extend(comp)

    assert(len(paragraphs) == len(recovered_papras))

    return recovered_papras

# target = tranlate(source, "en2zh")

class WikiTextCleaner(object):
    """docstring for WikiTextCleaner"""
    def __init__(self):
        super(WikiTextCleaner, self).__init__()

    def build_inner_pattern(self):
        # skip patterns
        curly_braces = re.compile("^\{\{.+?\}\}")
        title = re.compile("^(={2,6}).+?\\1")

        # remove patterns
        ref0 = re.compile("<ref.*?>.+?</ref>")
        ref1 = re.compile("<ref.*?/>")
        # self.refs = [ref0, ref1]
        syntax_bold = re.compile("'{2,5}")
        syntax_order = re.compile("^\*.+")
        syntax_orderless = re.compile("^#")
        syntax_def = re.compile("^;")
        syntax_indent = re.compile("^:+")
        syntax_braces = re.compile("\{\{.+?\}\}")

        self.skip_pattern = [curly_braces, title, syntax_order]
        self.syntax_pattern = [ref0, ref1, syntax_bold, 
            syntax_orderless, syntax_def, syntax_indent, syntax_braces]

        self.syntax_link = re.compile("\[\[.+?\]\]")
        self.inlinked = re.compile("\[\[(.+\|)?(.+)\]\]")

        self.html_tag = re.compile("<(\w+)>(.+)</\1>")

    def __call__(self, text_lines):
        self.build_inner_pattern()

        ret_lines = []
        if_skiped = []

        for i, l in enumerate(text_lines):
            if self._check_skip(l):
                ret_lines.append("")
                continue

            ret_lines.append(self._clear_syntax(l))

        return ret_lines

    def _check_skip(self, text):
        text = text.strip()
        for patt in self.skip_pattern:
            if patt.fullmatch(text):
                return True

        return False

    def _clear_syntax(self, text):
        # 替换ref
        # for ref in self.refs:
        #     text = ref.sub("", text)

        for patt in self.syntax_pattern:
            text = patt.sub("", text)

        # 解决[[]] 问题
        all_matched = self.syntax_link.findall(text)

        if all_matched:
            all_title = []
            for m in all_matched:
                all_title.append(self.inlinked.match(m).group(2))

            for m, s in zip(all_matched, all_title):
                text = text.replace(m, s)

        return text


if __name__ == '__main__':
    cleaner = WikiTextCleaner()

    input_file = sys.argv[1]
    with open(input_file) as f:
        content = f.readlines()
    clean_text = cleaner(content)

    trans_lines = translate_passage(clean_text, "en2zh")

    with open(input_file + ".out", "w+") as w:
        for s, t, in zip(content, trans_lines):
            w.write(s)

            if t.strip():
                w.write(t + "\n")
