<template>
  <el-config-provider :locale="locale">
    <router-view />
  </el-config-provider>
</template>

<script setup>
import locale from 'element-plus/es/locale/lang/zh-cn'
</script>

<style>
:root {
  --bg: #f5f5f7;
  --panel: rgba(255, 255, 255, 0.82);
  --panel-strong: #ffffff;
  --panel-soft: #fbfbfd;
  --line: rgba(15, 23, 42, 0.08);
  --line-strong: rgba(15, 23, 42, 0.12);
  --text: #111827;
  --muted: #6b7280;
  --accent: #0071e3;
  --accent-soft: rgba(0, 113, 227, 0.08);
  --success: #34a853;
  --danger: #d92d20;
  --shadow: 0 12px 36px rgba(15, 23, 42, 0.08);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  background:
    radial-gradient(circle at top left, rgba(0, 113, 227, 0.06), transparent 22%),
    radial-gradient(circle at bottom right, rgba(255, 255, 255, 0.85), transparent 30%),
    linear-gradient(180deg, #f7f8fa 0%, #f3f4f6 100%);
  color: var(--text);
}

body {
  color: var(--text);
}

a {
  color: inherit;
}

.el-card {
  background: var(--panel) !important;
  border: 1px solid var(--line) !important;
  box-shadow: var(--shadow) !important;
  border-radius: 24px !important;
  color: var(--text) !important;
  backdrop-filter: blur(18px);
}

.page-shell {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.surface-card {
  padding: 2px;
  border-radius: 26px;
}

.page-title {
  font-size: 26px;
  font-weight: 700;
  letter-spacing: -0.03em;
  color: #111827;
}

.page-subtitle {
  margin-top: 4px;
  font-size: 14px;
  line-height: 1.7;
  color: #667085;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.card-header > span,
.card-header > strong {
  font-size: 18px;
  font-weight: 650;
  color: #111827;
  letter-spacing: -0.02em;
}

.toolbar-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.search-form {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px 10px;
  margin-bottom: 6px;
}

.search-form .el-form-item {
  margin-bottom: 10px !important;
  margin-right: 0 !important;
}

.search-form .el-input,
.search-form .el-select,
.search-form .el-date-editor,
.search-form .el-input-number {
  min-width: 180px;
}

.search-form .el-select .el-input__wrapper,
.search-form .el-input .el-input__wrapper,
.search-form .el-date-editor.el-input__wrapper {
  min-width: 180px;
}

.el-dialog .el-select,
.el-dialog .el-date-editor,
.el-dialog .el-input,
.el-dialog .el-textarea {
  width: 100%;
}

.el-card__body,
.el-card__header,
.el-table,
.el-form,
.el-form-item,
.el-descriptions,
.el-descriptions__body,
.el-empty,
.el-timeline {
  color: var(--text) !important;
}

.el-card__header {
  border-bottom: 1px solid var(--line) !important;
  padding: 20px 24px !important;
}

.el-card__body {
  padding: 22px 24px !important;
}

.el-table {
  --el-table-border-color: var(--line) !important;
  --el-table-header-bg-color: rgba(245, 247, 250, 0.8) !important;
  --el-table-tr-bg-color: transparent !important;
  --el-table-row-hover-bg-color: rgba(0, 113, 227, 0.04) !important;
  --el-table-text-color: var(--text) !important;
  --el-table-header-text-color: #374151 !important;
  background: transparent !important;
  color: var(--text) !important;
}

.el-table th.el-table__cell,
.el-table tr,
.el-table td.el-table__cell {
  background: transparent !important;
}

.el-table__cell {
  padding-top: 14px !important;
  padding-bottom: 14px !important;
}

.el-table .cell {
  line-height: 1.45;
  display: block;
}

.el-table__header-wrapper th:last-child .cell,
.el-table__body-wrapper td:last-child .cell,
.operation-column .cell {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
  text-align: center;
}

.el-table .el-button.is-link,
.el-table .el-button--text {
  margin: 0 !important;
  padding: 0 2px !important;
}

.el-table .el-tag {
  border-radius: 999px;
  padding: 0 10px;
}

.el-table th.el-table__cell {
  font-weight: 600;
}

.el-table td.el-table__cell {
  vertical-align: middle;
}

.el-input__wrapper,
.el-textarea__inner,
.el-select .el-input__wrapper,
.el-date-editor.el-input__wrapper,
.el-input-number,
.el-input-number .el-input__wrapper {
  background: rgba(255, 255, 255, 0.92) !important;
  box-shadow: 0 0 0 1px var(--line) inset !important;
  color: var(--text) !important;
}

.el-input__inner,
.el-textarea__inner {
  color: var(--text) !important;
}

.el-input__inner::placeholder,
.el-textarea__inner::placeholder {
  color: #9aa3b2 !important;
}

.el-form-item__label,
.el-radio,
.el-checkbox,
.el-descriptions__label,
.el-descriptions__content,
.el-pagination,
.el-breadcrumb__inner,
.el-dropdown,
.el-tag,
.el-tabs__item {
  color: var(--text) !important;
}

.el-dialog {
  background: var(--panel-strong) !important;
  border: 1px solid var(--line-strong);
  border-radius: 28px !important;
  box-shadow: var(--shadow) !important;
}

.el-dialog__title,
.el-drawer__title {
  color: var(--text) !important;
}

.el-message {
  border-radius: 16px !important;
  background: rgba(255, 255, 255, 0.96) !important;
  border: 1px solid var(--line) !important;
}

.el-button--primary {
  --el-button-bg-color: var(--accent) !important;
  --el-button-border-color: var(--accent) !important;
  --el-button-hover-bg-color: #1783f8 !important;
  --el-button-hover-border-color: #1783f8 !important;
  --el-button-active-bg-color: #0062c4 !important;
  --el-button-active-border-color: #0062c4 !important;
  --el-button-text-color: #ffffff !important;
  border-radius: 999px !important;
}

.el-button:not(.el-button--primary) {
  background: rgba(255, 255, 255, 0.9);
  border-color: var(--line);
  color: var(--text);
  border-radius: 999px;
}

.el-pagination {
  justify-content: flex-end;
  margin-top: 18px;
}

.el-button--text,
.el-button.is-link {
  color: #2563eb !important;
}

.el-select-dropdown,
.el-picker-panel,
.el-dropdown-menu,
.el-message-box {
  background: #ffffff !important;
  border-color: var(--line) !important;
  color: var(--text) !important;
}

.el-message-box__title,
.el-message-box__message,
.el-select-dropdown__item,
.el-dropdown-menu__item {
  color: var(--text) !important;
}

.el-empty__description p {
  color: var(--muted) !important;
}

.el-menu {
  border-right: none !important;
}
</style>
