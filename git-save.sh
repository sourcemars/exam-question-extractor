#!/bin/bash

# Git 快速提交脚本 - 个人项目专用
# 用法: ./git-save.sh "提交说明"
# 示例: ./git-save.sh "添加批量处理功能"

# 检查是否提供了提交信息
if [ -z "$1" ]; then
    echo "❌ 错误: 请提供提交说明"
    echo "用法: ./git-save.sh \"你的提交说明\""
    echo "示例: ./git-save.sh \"修复通义千问 API 超时问题\""
    exit 1
fi

COMMIT_MESSAGE="$1"

echo "============================================"
echo "🚀 Git 快速提交流程"
echo "============================================"
echo ""

# 1. 显示当前修改
echo "📝 当前修改的文件:"
git status --short
echo ""

# 2. 添加所有修改
echo "➕ 添加所有修改到暂存区..."
git add .

# 3. 提交
echo "💾 提交修改..."
git commit -m "$COMMIT_MESSAGE

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

if [ $? -ne 0 ]; then
    echo "❌ 提交失败"
    exit 1
fi

# 4. 推送到 GitHub
echo "⬆️  推送到 GitHub..."
git push

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================"
    echo "✅ 代码已成功保存到 GitHub！"
    echo "============================================"
    echo ""
    echo "📊 最近的提交记录:"
    git log --oneline -3
    echo ""
else
    echo "❌ 推送失败，请检查网络连接"
    exit 1
fi
