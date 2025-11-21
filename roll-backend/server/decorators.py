import mimetypes
import json
import os
from functools import wraps

def auto_content_type(cls):
    """
    自动为API类的响应方法注入Content-Type头的装饰器
    """
    original_vercel_register = cls.vercel

    @wraps(original_vercel_register)
    def vercel_handler(**kwargs):
        if "response" in kwargs:
            original_send_file = kwargs["response"].send_file
            original_send_text = kwargs["response"].send_text
            original_send_json = kwargs["response"].send_json

            @wraps(original_send_file)
            def enhanced_send_file(self, filepath):
                # 自动检测并设置Content-Type
                content_type, _ = mimetypes.guess_type(filepath)
                if content_type:
                    self.send_header('Content-Type', content_type)
                return original_send_file(self, filepath)

            @wraps(original_send_text)
            def enhanced_send_text(self, text):
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                return original_send_text(self, text)

            @wraps(original_send_json)
            def enhanced_send_json(self, data):
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                return original_send_json(self, data)
            
            kwargs["response"].send_file = enhanced_send_file
            kwargs["response"].send_text = enhanced_send_text
            kwargs["response"].send_json = enhanced_send_json
        
        return original_vercel_register(**kwargs)

    cls.vercel = vercel_handler

    return cls


def hot_reload(cls):
    """
    为API类启用热重载功能的装饰器
    """
    cls.hot_reload = True
    return cls
