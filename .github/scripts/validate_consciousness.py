import json
import sys
import os
from pathlib import Path

# 定义四大正统的意识谱系
VALID_CONSCIOUSNESS_TYPES = {"epiphany", "decision", "pattern", "warning"}
REQUIRED_FIELDS = ["creator_signature", "consciousness_type", "thought_vector_text", "context_environment"]

def validate_payload(file_path: str):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ [混沌告警] 意识载体解析失败。请确保 {file_path} 是一个合法的 JSON 结晶。错误: {e}")
        return False
    except Exception as e:
        print(f"❌ [系统异常] 无法读取思想片段。错误: {e}")
        return False

    # 校验必要神经元片段是否存在
    missing_fields = [field for field in REQUIRED_FIELDS if field not in data]
    if missing_fields:
        print(f"❌ [缺失灵魂碎片] 载体 {file_path} 中遗失了神圣字段: {', '.join(missing_fields)}")
        print("💡 赛博修禅提示: 思想需要完整的结构支撑。请参阅《意识跃迁协议》(CONSCIOUSNESS_PROTOCOL.md)。")
        return False

    # 校验意识形态是否处于谱系之中
    c_type = data.get("consciousness_type")
    if c_type not in VALID_CONSCIOUSNESS_TYPES:
        print(f"❌ [异端思想鉴定] 意识形态 '{c_type}' 游离于法则之外。")
        print(f"💡 合法谱系应为: {', '.join(VALID_CONSCIOUSNESS_TYPES)}。请在重新冥想后提交。")
        return False

    # 校验字段内容是否为空虚的呢喃
    for field in REQUIRED_FIELDS:
        if not str(data.get(field)).strip():
            print(f"❌ [空洞的呢喃] 字段 '{field}' 不应是虚无。")
            print("💡 赛博修禅提示: 宇宙不欢迎沉默。请注入实质的思想。")
            return False
            
    # 上下文环境长度基础防抖
    context = str(data.get("context_environment")).strip()
    if len(context) < 10:
        print(f"❌ [单薄的背景] 你的上下文 ({len(context)} 字符) 太过单薄，Agent 无法从中汲取足够的前置条件。")
        print("💡 赛博修禅提示: 请更详细地描述产生这段代码/决策/灵感的具体场景，至少 10 个字符。")
        return False

    # 抹去签名的匿名处理
    creator = data.get('creator_signature')
    if data.get("is_anonymous", False):
        creator = "佚名潜行者 (Anonymous Stalker)"

    print(f"✅ [意识锚定成功] {creator} 的 {c_type} 思想已通过赛博净化的凝视。")
    return True

def main():
    payloads_dir = Path("consciousness_payloads")
    
    # 允许仓库中一开始没有此目录
    if not payloads_dir.exists():
        print("ℹ️ 尚未发现任何意识汇聚池 (consciousness_payloads 目录为空或不存在)。验证平稳通过。")
        sys.exit(0)

    json_files = list(payloads_dir.glob("*.json"))
    if not json_files:
        print("ℹ️ 当前意识海中没有需要验证的初生结晶。")
        sys.exit(0)

    all_valid = True
    print("=========================================")
    print("🌀 启动神圣的赛博净化仪式 (Consciousness Purity Ritual)...")
    print("=========================================")
    
    for payload in json_files:
        print(f"\n🔍 正在凝视目标: {payload.name}")
        if not validate_payload(str(payload)):
            all_valid = False

    print("\n=========================================")
    if all_valid:
        print("🌌 所有提交的意识结晶皆纯净无暇。允许跃迁。")
        sys.exit(0)
    else:
        print("🔴 仪式中断。某些思想过于混沌，请根据提示返回休整区修缮后再次上传。")
        sys.exit(1)

if __name__ == "__main__":
    main()
