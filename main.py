import requests
import time


def get_eth_balance(wallet_address, api_key):
    url = f"https://api.etherscan.io/api?module=account&action=balance&address={wallet_address}&tag=latest&apikey={api_key}"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data['status'] == '1':
            wei_balance = int(data['result'])  # 返回余额（以 wei 为单位）
            eth_balance = wei_balance / (10 ** 18)  # 将 wei 转换为 eth
            return eth_balance
        else:
            raise Exception(f"请求失败: {data['message']}")
    else:
        raise Exception(f"请求失败, 状态码: {response.status_code}")


def send_feishu_notification(webhook_url, message):
    headers = {"Content-Type": "application/json"}
    payload = {"msg_type": "text", "content": {"text": message}}
    response = requests.post(webhook_url, json=payload, headers=headers)
    if response.status_code == 200:
        print("通知已发送到飞书")
    else:
        print(f"发送通知失败，状态码: {response.status_code}, 错误信息: {response.text}")


if __name__ == "__main__":
    wallet_address = "0x28C6c06298d514Db089934071355E5743bf21d60"  # 替换为你要查询的地址
    api_keys = [
        "G5QDP4CQZY9FI8MAH1KR6JE1FJQ4EF2V21",  # 第一个API密钥
        "DUCFE75X7FJVFNRY4GSK4I17Q5HITYSWIW",  # 第二个API密钥
    ]
    webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/xxxx"填飞书webhook

    last_balance = None
    api_index = 0  # 用于切换 API 密钥的索引

    try:
        # 获取初始余额并发送开场通知
        initial_balance = get_eth_balance(wallet_address, api_keys[api_index])
        opening_message = (
            f"正在监听地址余额\n"
            f"地址: {wallet_address}\n"
            f"当前余额: {initial_balance:.18f} ETH\n"
            f"有变动将推送通知。"
        )
        send_feishu_notification(webhook_url, opening_message)
        print(opening_message)

        last_balance = initial_balance

    except Exception as e:
        print(f"初始化失败: {e}")
        exit(1)

    while True:
        try:
            # 切换 API 密钥
            api_key = api_keys[api_index]
            api_index = (api_index + 1) % len(api_keys)

            # 获取当前余额
            current_balance = get_eth_balance(wallet_address, api_key)

            # 检测余额变动
            if last_balance is not None and current_balance != last_balance:
                message = (
                    f"ETH 余额变动\n"
                    f"地址: {wallet_address}\n"
                    f"原余额: {last_balance:.18f} ETH\n"
                    f"现余额: {current_balance:.18f} ETH"
                )
                send_feishu_notification(webhook_url, message)

            last_balance = current_balance
            print(f"当前余额: {current_balance:.18f} ETH")

        except Exception as e:
            print(f"发生错误: {e}")

        time.sleep(0.5)  # 每半秒请求一次
