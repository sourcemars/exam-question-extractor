#!/bin/bash

# GitHub Release 创建脚本
# 用法: ./release.sh <版本号> <版本说明>
# 示例: ./release.sh v1.0.0 "初始版本，支持通义千问"

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "❌ 用法错误"
    echo ""
    echo "用法: ./release.sh <版本号> <版本说明>"
    echo ""
    echo "示例:"
    echo "  ./release.sh v1.0.0 \"初始版本，支持通义千问\""
    echo "  ./release.sh v1.1.0 \"添加批量处理功能\""
    echo "  ./release.sh v1.0.1 \"修复 API 超时问题\""
    echo ""
    echo "版本号规范:"
    echo "  v主版本.次版本.修订号"
    echo "  - 主版本: 重大更新，不兼容"
    echo "  - 次版本: 新功能，兼容"
    echo "  - 修订号: Bug 修复"
    exit 1
fi

VERSION="$1"
DESCRIPTION="$2"

echo "============================================"
echo "🚀 创建 GitHub Release"
echo "============================================"
echo ""
echo "版本号: $VERSION"
echo "说明: $DESCRIPTION"
echo ""

# 1. 检查是否有未提交的修改
if [[ -n $(git status -s) ]]; then
    echo "⚠️  检测到未提交的修改"
    echo ""
    git status --short
    echo ""
    read -p "是否先提交这些修改？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "➕ 添加修改..."
        git add .
        read -p "请输入提交信息: " commit_msg
        git commit -m "$commit_msg"
        echo "⬆️  推送到 GitHub..."
        git push
    else
        echo "❌ 请先处理未提交的修改"
        exit 1
    fi
fi

# 2. 确认创建 Release
echo ""
read -p "确认创建 Release $VERSION？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 已取消"
    exit 1
fi

# 3. 创建标签
echo ""
echo "🏷️  创建标签 $VERSION..."
git tag -a "$VERSION" -m "Release $VERSION: $DESCRIPTION

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

if [ $? -ne 0 ]; then
    echo "❌ 标签创建失败（可能已存在）"
    exit 1
fi

# 4. 推送标签
echo "⬆️  推送标签到 GitHub..."
git push origin "$VERSION"

if [ $? -ne 0 ]; then
    echo "❌ 标签推送失败"
    # 删除本地标签
    git tag -d "$VERSION"
    exit 1
fi

echo ""
echo "============================================"
echo "✅ Release 标签创建成功！"
echo "============================================"
echo ""
echo "📌 下一步："
echo ""
echo "方式 1 - 网页创建 Release (推荐):"
echo "  访问: https://github.com/sourcemars/exam-question-extractor/releases/new?tag=$VERSION"
echo ""
echo "方式 2 - 使用 GitHub CLI:"
echo "  gh release create $VERSION --title \"$VERSION\" --notes \"$DESCRIPTION\""
echo ""
echo "📊 当前所有版本:"
git tag -l
echo ""
