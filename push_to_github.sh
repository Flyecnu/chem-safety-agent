#!/bin/bash
# 推送代码到 GitHub 仓库（使用 Flyecnu 账号的 SSH 密钥）
# 使用方法：./push_to_github.sh [commit_message]

# 配置
SSH_KEY="$HOME/.ssh/id_ed25519_flyecnu"
REPO_URL="git@github.com:Flyecnu/chem-safety-agent.git"

# 检查是否有修改
if [ -z "$(git status --porcelain)" ]; then
    echo "📭 工作区干净，无需提交"
else
    # 如果提供了 commit message，则提交
    if [ -n "$1" ]; then
        echo "📝 提交更改..."
        git add .
        git commit -m "$1

Co-Authored-By: Claude <noreply@anthropic.com>"
    else
        echo "⚠️  有未提交的更改，请提供 commit message："
        echo "   ./push_to_github.sh \"your commit message\""
        exit 1
    fi
fi

echo "🚀 推送到 GitHub..."
echo "📦 仓库: $REPO_URL"
echo ""

# 使用指定的 SSH 密钥推送
GIT_SSH_COMMAND="ssh -i $SSH_KEY -o IdentitiesOnly=yes" git push origin master

echo ""
echo "✅ 推送完成！"
echo "🔗 访问你的仓库: https://github.com/Flyecnu/chem-safety-agent"
