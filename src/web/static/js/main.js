/**
 * 题库系统前端脚本
 */

document.addEventListener('DOMContentLoaded', function() {
    // 初始化
    initFilters();
    initKeyboardNavigation();
});

/**
 * 初始化筛选功能
 */
function initFilters() {
    // 筛选条件变化时自动提交（可选功能，默认关闭）
    const autoSubmit = false;

    if (autoSubmit) {
        const filterSelects = document.querySelectorAll('select[name="type"], select[name="difficulty"]');
        filterSelects.forEach(function(select) {
            select.addEventListener('change', function() {
                this.form.submit();
            });
        });
    }
}

/**
 * 初始化键盘导航
 */
function initKeyboardNavigation() {
    document.addEventListener('keydown', function(e) {
        // 只在详情页启用键盘导航
        const prevLink = document.querySelector('a[href*="question/"]:has(svg path[d*="15 19l-7-7"])');
        const nextLink = document.querySelector('a[href*="question/"]:has(svg path[d*="9 5l7 7"])');

        // 左箭头 - 上一题
        if (e.key === 'ArrowLeft' && !e.ctrlKey && !e.metaKey) {
            const prevBtn = document.querySelector('a[href*="question_detail"]:first-of-type, a:contains("上一题")');
            // 使用更通用的选择器
            const links = document.querySelectorAll('a');
            links.forEach(function(link) {
                if (link.textContent.includes('上一题')) {
                    link.click();
                }
            });
        }

        // 右箭头 - 下一题
        if (e.key === 'ArrowRight' && !e.ctrlKey && !e.metaKey) {
            const links = document.querySelectorAll('a');
            links.forEach(function(link) {
                if (link.textContent.includes('下一题')) {
                    link.click();
                }
            });
        }
    });
}

/**
 * 显示/隐藏答案（可选功能）
 */
function toggleAnswer(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.classList.toggle('hidden');
    }
}

/**
 * 复制题目内容到剪贴板
 */
function copyQuestion(questionText) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(questionText).then(function() {
            showToast('已复制到剪贴板');
        }).catch(function(err) {
            console.error('复制失败:', err);
        });
    }
}

/**
 * 显示提示消息
 */
function showToast(message, duration = 2000) {
    const toast = document.createElement('div');
    toast.className = 'fixed bottom-4 right-4 bg-gray-800 text-white px-4 py-2 rounded-lg shadow-lg z-50';
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(function() {
        toast.remove();
    }, duration);
}
