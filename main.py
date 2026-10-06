# main.py
from YouKa import process_user
import os

def main():
    tokens_env = os.getenv("HANXILU_TOKENS", "")
    if tokens_env:
        tokens = []
        for part in tokens_env.replace('\n', ',').split(','):
            part = part.strip()
            if part:
                tokens.append(part)
    else:
        # 测试用硬编码，请替换
        tokens = [
            "xxxxxx",
        ]

    if not tokens:
        print("没有提供任何 token，请设置环境变量 HANXILU_TOKENS")
        return

    for idx, token in enumerate(tokens, 1):
        print(f"\n========== 处理第 {idx} 个用户 ==========")
        res = process_user(token)
        if res["success"]:
            print(f"用户ID: {res['uid']}")
            contact = res['user_info'].get('email') or res['user_info'].get('phone') or '无'
            print(f"联系方式: {contact}")
            print(f"昵称: {res['user_info'].get('nickname')}")
            print(f"等级: {res['user_info'].get('grade')}")
            print(f"积分: {res['user_info'].get('integral')}")
            print(f"经验: {res['user_info'].get('exp')}")
            print(f"📅 当前连续签到天数：{res['continuous_days']} 天")
            print(f"📋 最近签到序列长度：{res['total_sign_days']} 天")
            # 新增：距离下一个奖励
            if res['next_reward_days'] > 0:
                print(f"🎯 距离下一个奖励还差 {res['next_reward_days']} 天 → {res['next_reward_info']}")
            else:
                print(f"🏆 {res['next_reward_info']}")

            if 'msg' in res['sign_in_reward']:
                print(f"签到结果: {res['sign_in_reward']['msg']}")
            else:
                reward = res['sign_in_reward']
                print(f"签到奖励: 积分+{reward.get('integral',0)}, 经验+{reward.get('exp',0)}, 优惠券+{reward.get('coupons',0)}")
        else:
            print(f"处理失败: {res['error']}")

if __name__ == "__main__":
    main()