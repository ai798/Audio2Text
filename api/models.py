import json

from django.db import models
from django.http import JsonResponse
import pickle


# Create your models here.


class VideoContent():

    def __init__(self, video_no: str, video_type: str, video_title: str, video_desc: str, video_content: str):
        self.video_no = video_no
        self.video_type = video_type
        self.video_title = video_title
        self.video_desc = video_desc
        self.video_content = video_content

    def serialize(self):
        return {
            'video_no': self.video_no,
            'video_type': self.video_type,
            'video_title': self.video_title,
            'video_desc': self.video_desc,
            'video_content': self.video_content,
        }


class VideoContentEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, VideoContent):
            return {'video_no': obj.video_no,
                    'video_type': obj.video_type,
                    'video_title': obj.video_title,
                    'video_desc': obj.video_desc,
                    'video_content': obj.video_content,
                    }
        return json.JSONEncoder.default(self, obj)


def SucResponse(**kwargs):
    if kwargs:
        resp_json = { 'payload': kwargs,
                      'errCode': 0,
                      'errMsg': "suc"
                      }
    else:
        resp_json = {
                     'errCode': 0,
                     'errMsg': "suc"
                     }
    return JsonResponse(resp_json)
