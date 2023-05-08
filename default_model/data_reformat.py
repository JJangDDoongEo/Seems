from _init import *

import random

from commons import file_util
from transformers import BertTokenizer

class DataReformator:
    def __init__(self):
        self.data_reformats = []
        self.delim = '\t'

    def load_folder(self, in_path: str, encoding: str, delim: str):
        in_file_paths = file_util.get_file_paths(in_path, True)
        for in_file_path in in_file_paths:
            self.load_file(in_file_path, encoding, delim)
            

    def load_file(self, in_file_path, encoding: str, delim: str):
        self.delim = delim
        in_file = file_util.open_file(in_file_path, encoding,'r')

        while 1:
            line = in_file.readline()
            if not line:
                break

            line = line.strip()
            if len(line) == 0:
                continue

            self.data_reformats.append(line)

        in_file.close()

    def div_reformat(self, train_val: int, val_val: int, test_val: int, is_shuffle: bool):
        if is_shuffle:
            datas = []
            datas.extend(self.data_reformats)
            random.shuffle(datas)            
        else:
            datas = self.data_reformats
        
        text_list = []
        label_list = []
        for term in datas:
            temp = term.split(self.delim)

            if len(temp) != 2:
                continue

            text_list.append(temp[0])
            label_list.append(temp[1])
        
        text_datas = self._div_reformat(text_list, train_val, val_val, test_val)
        label_datas = self._div_reformat(label_list, train_val, val_val, test_val)

        [text_datas[0], label_datas[0]]
        [text_datas[1], label_datas[1]]
        [text_datas[2], label_datas[2]]

        return [[text_datas[0], label_datas[0]],
                [text_datas[1], label_datas[1]],
                [text_datas[2], label_datas[2]]]

    
    def _div_reformat(self, datas, train_val: int, val_val: int, test_val: int):
        data_len = len(datas)

        train_size = int(data_len * (train_val *0.1))
        train_data = datas[ : train_size]

        val_size = int(data_len * (val_val * 0.1))
        val_data = datas[train_size : train_size+val_size]
        
        # test_val 값은 굳이 사용하지 않아도 된다. (남은 항목을 다 가져오면 되므로)
        test_data = datas[train_size+val_size:]

        return [train_data, val_data, test_data]


    def reformating(self, datas, bert_model_name, max_len):       
        tokenizer = BertTokenizer.from_pretrained(bert_model_name)

        data_xs = []
        data_ys = []

        data_len = len(datas[0])
        for i in range(data_len):
            text = datas[0][i]                                                                              # text (우리가 넘겨주는 하나의 입력)
            label = datas[1][i]                                                                             # label (대응되는 하나의 레이블)

            encoded = tokenizer.encode(text, truncation=True, padding='max_length', max_length=max_len)     # token_ids
            num_zeros = encoded.count(0)
            mask = [1] * (max_len - num_zeros) + [0] * num_zeros                                            # attention_mask
            segment = [0]*max_len                                                                           # token_type_ids

            data_xs.append([encoded, mask, segment])
            data_ys.append(label)
        
        return [data_xs, data_ys]
    
    ## 우리가 입력으로 넣은 텍스트는 실제 버트 모델의 입력으로 사용되는 것이 아니라, 실제 버트 모델이 사용하는 입력의 형태로 변환해서 넘겨줘야 함
    ##  - 입력 텍스트 : 1###이건테스
    ##  - 변환된 입력 : [[2, 21, 7, 7, 7, 5370, 10814, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # token_ids
    #                    [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],          # attention_mask
    #                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]          # token_type_ids
    # 위 변환된 입력이 하나의 x이고, 대응되는 y는 '0' 또는 '1'

    # 실제로 우리가 넘겨주는 형식 -> text : label
    #   - Ex). 
    #           x : ###이건테스
    #           y : 0 

    # 하지만, 우리가 넘겨준 text('###이건테스')를 버트의 입력([token_ids, attention_mask, token_type_ids])으로 변환해야 함
    #   - Ex). [ [2, 21, 7, 7, 7, 5370, 10814, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #            [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] ]

    # 결국 버트에 들어가는 x, y 형식은 [token_ids, attention_mask, token_type_ids] : label 과 같다.
    #   - Ex). 
    #           x : [ [2, 21, 7, 7, 7, 5370, 10814, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] ]
    #           y : 0