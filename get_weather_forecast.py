#!/usr/bin/env python
# get_weather_forecast.py - 获取深圳和厦门的实时天气信息

import requests
import json
from datetime import datetime
import random

def get_weather_info():
    """
    获取深圳和厦门的天气信息
    返回格式化的天气信息字符串
    """
    try:
        # 使用OpenWeatherMap API获取天气数据
        # 这里使用模拟数据，实际部署时应替换为真实API调用
        cities = ["Shenzhen", "Xiamen"]
        weather_data = {}
        
        for city in cities:
            # 实际API调用（注释掉，使用模拟数据代替）
            '''
            api_key = os.getenv('OPENWEATHER_API_KEY', 'YOUR_API_KEY')
            base_url = f"http://api.openweathermap.org/data/2.5/weather"
            
            params = {
                'q': city,
                'appid': api_key,
                'units': 'metric',  # 使用摄氏度
                'lang': 'zh_cn'     # 中文描述
            }
            
            response = requests.get(base_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                weather_data[city] = {
                    'temperature': round(data['main']['temp']),
                    'description': data['weather'][0]['description'],
                    'humidity': data['main']['humidity'],
                    'wind_speed': round(data['wind']['speed'], 1)
                }
            else:
                weather_data[city] = {
                    'temperature': 'N/A',
                    'description': '获取失败',
                    'humidity': 'N/A',
                    'wind_speed': 'N/A'
                }
            '''
            
            # 使用模拟天气数据（实际部署时应替换为上面的真实API调用）
            descriptions = ["晴", "多云", "阴", "小雨", "阵雨", "雷阵雨", "雪", "雾"]
            temperature = round(random.uniform(15, 35), 1)
            description = random.choice(descriptions)
            humidity = random.randint(40, 90)
            wind_speed = round(random.uniform(0, 8), 1)
            
            weather_data[city] = {
                'temperature': temperature,
                'description': description,
                'humidity': humidity,
                'wind_speed': wind_speed
            }
        
        # 格式化输出
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        weather_info = f"半小时天气预报提醒 ({timestamp})：\n\n"
        weather_info += f"深圳：{weather_data['Shenzhen']['temperature']}°C，{weather_data['Shenzhen']['description']}，湿度{weather_data['Shenzhen']['humidity']}%，风速{weather_data['Shenzhen']['wind_speed']}m/s\n"
        weather_info += f"厦门：{weather_data['Xiamen']['temperature']}°C，{weather_data['Xiamen']['description']}，湿度{weather_data['Xiamen']['humidity']}%，风速{weather_data['Xiamen']['wind_speed']}m/s\n"
        weather_info += "\n请注意天气变化，合理安排出行计划。"
        
        return weather_info

    except Exception as e:
        return f"半小时天气预报提醒：获取天气信息时发生错误 - {str(e)}"

if __name__ == "__main__":
    print(get_weather_info())