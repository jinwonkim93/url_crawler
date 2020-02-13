#-*- coding:utf-8 -*-
import os
import subprocess
import re
from pandas import DataFrame
import pandas as pd
import sys
from enum import Enum
from typing import Dict, Tuple
from image_generator import ImageGenerator


class RegexLibrary(Enum):
    website = r"Running \d+. test @ https?://(.+?)[/\n]"
    req_s = r" *Requests/sec: +(\d+\.?\d*)"
    latency = r" +(\d+\.?\d*)% +(\d+\.?\d*)(\w+)"
    detailed_latency = r" +([\d\.]+) +([\d\.]+) +[\d\.]+ +[\d\.inf]+\n"
    split = r"Running \d+. test .+?Transfer\/sec: +\d+\.?\d*\w+"
    split_after_transfer = r" *Transfer\/sec: +\d+\.?\d*\w+(\n)"


class UnitMultiplier(Enum):
    s = 1
    ms = 1e-3
    us = 1e-6
    ns = 1e-9

def convert_k(str:str) -> hex:
    result = ''
    for letter in str:
        result = result + '%' + hex(letter)[2:].upper()
    return result

def run_wrk(keyword: str, crawl_type: str) -> str:
    duration = 20
    tread_num = 1
    connection_num = 1
    url = 'http://localhost:5000/'+crawl_type+'/'
    wait_time = 60
    keyword = convert_k(keyword.encode('utf-8'))
    print(url+keyword)
    data = subprocess.check_output(f'wrk --latency -d{duration}s -t{tread_num} -c{connection_num} {url}{keyword} --timeout {wait_time}s'.split())
    return data.decode('utf-8')

def extract_data(datas: list, curve_names: list = None) -> Tuple[Dict[str, Dict[float,float]], str]:
    std = []
    for line in datas:
        std.append(line)
    std_concat = "".join(std)    
    all_wrk_output = re.findall(RegexLibrary.split.value, std_concat, flags=re.DOTALL)
    parsed = {}  # type: Dict[str, Dict[float, float]]
    websites = []
    for i, single_wrk_output in enumerate(all_wrk_output):
                websites.append(re.search(RegexLibrary.website.value, single_wrk_output).group(1))
                req_s = float(re.search(RegexLibrary.req_s.value, single_wrk_output).group(1))
                print(websites)
                print(req_s)
                if curve_names is not None and i < len(curve_names):
                    label = curve_names[i]
                else:
                    label = "{} req/s".format(req_s)
                parsed[label] = {}

                for matches in re.findall(RegexLibrary.latency.value, single_wrk_output):
                    percentile, result, unit = matches
                    print(matches)
                    scaled_result = round(float(result) * UnitMultiplier[unit].value, 9)
                    parsed[label][float(percentile)] = scaled_result


                for matches in re.findall(RegexLibrary.detailed_latency.value, single_wrk_output):
                    result, percentile = matches
                    percentile = float(percentile) * 100
                    scaled_result = round(float(result) * UnitMultiplier.ms.value, 9)
                    parsed[label][percentile] = scaled_result
    
    if len(set(websites)) == 0:
        raise ValueError("No website detected")
    if len(set(websites)) > 1:
        raise ValueError("Multiple different website detected in log")
    else:
        website = websites[0]
    
    return parsed, website
    

def run_test():
    keywords = ['apple','blue', '안녕', 'money']
    #keywords = ['monday']
    
    for crawl_type in ['sync', 'async']:
        datas = []
        for keyword in keywords:
            data = run_wrk(keyword,crawl_type)
            datas.append(data) 
        extracted_datas, website = extract_data(datas, keywords)
        image_generator = ImageGenerator(crawl_type)
        image_name = 'static/' + crawl_type + '_image.png'
        image_generator.generate_and_save_image(extracted_datas, website, image_name, latency_until=100)