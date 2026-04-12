<template>
  <el-config-provider :locale="locale">
    <router-view />
  </el-config-provider>
</template>

<script setup>
import locale from 'element-plus/es/locale/lang/zh-cn'
</script>

<style>
/* 引入统一设计规范 */
@import './design-system.css';

html, body, #app {
  height: 100%;
  background:
    radial-gradient(circle at top left, rgba(59, 130, 246, 0.08), transparent 24%),
    radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.92), transparent 30%),
    linear-gradient(180deg, var(--openexam-bg-secondary) 0%, var(--openexam-bg-tertiary) 100%);
}

.page-shell {
  display: flex;
  flex-direction: column;
  gap: var(--openexam-space-5);
}

.surface-card {
  padding: 2px;
  border-radius: var(--openexam-radius-2xl);
  position: relative;
}

.page-title {
  font-size: var(--openexam-font-2xl);
  font-weight: var(--openexam-font-bold);
  color: var(--openexam-text-primary);
  margin-bottom: var(--openexam-space-3);
}

.page-subtitle {
  margin-top: var(--openexam-space-1);
  font-size: var(--openexam-font-sm);
  line-height: 1.7;
  color: var(--openexam-text-secondary);
  max-width: 720px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--openexam-space-4);
}

.card-header > span,
.card-header > strong {
  font-size: var(--openexam-font-lg);
  font-weight: var(--openexam-font-semibold);
  color: var(--openexam-text-primary);
}

.toolbar-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--openexam-space-4);
  flex-wrap: wrap;
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: var(--openexam-space-3);
  flex-wrap: wrap;
}

.search-form {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--openexam-space-2) var(--openexam-space-3);
  margin-bottom: var(--openexam-space-2);
}

.search-form .el-form-item {
  margin-bottom: var(--openexam-space-3) !important;
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

/* 自定义 Element Plus 样式 */
.el-card {
  background: var(--openexam-bg-primary) !important;
  border: 1px solid var(--openexam-border) !important;
  box-shadow: var(--openexam-shadow-md) !important;
  border-radius: var(--openexam-radius-lg) !important;
  color: var(--openexam-text-primary) !important;
}

.el-card__header {
  border-bottom: 1px solid var(--openexam-border) !important;
  padding: var(--openexam-space-5) var(--openexam-space-6) !important;
}

.el-card__body {
  padding: var(--openexam-space-6) !important;
}

.el-table {
  --el-table-border-color: var(--openexam-border) !important;
  --el-table-header-bg-color: var(--openexam-bg-tertiary) !important;
  --el-table-tr-bg-color: transparent !important;
  --el-table-row-hover-bg-color: rgba(59, 130, 246, 0.04) !important;
  --el-table-text-color: var(--openexam-text-primary) !important;
  --el-table-header-text-color: var(--openexam-text-secondary) !important;
  background: transparent !important;
  color: var(--openexam-text-primary) !important;
}

.el-table th.el-table__cell,
.el-table tr,
.el-table td.el-table__cell {
  background: transparent !important;
}

.el-table__cell {
  padding-top: var(--openexam-space-4) !important;
  padding-bottom: var(--openexam-space-4) !important;
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
  gap: var(--openexam-space-2);
  flex-wrap: wrap;
  text-align: center;
}

.el-table .el-button.is-link,
.el-table .el-button--text {
  margin: 0 !important;
  padding: 0 2px !important;
}

.el-table .el-tag {
  border-radius: var(--openexam-radius-full);
  padding: 0 10px;
}

.el-table th.el-table__cell {
  font-weight: var(--openexam-font-semibold);
  font-size: var(--openexam-font-xs);
  letter-spacing: 0.06em;
  text-transform: uppercase;
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
  background: var(--openexam-bg-primary) !important;
  box-shadow: 0 0 0 1px var(--openexam-border) inset !important;
  color: var(--openexam-text-primary) !important;
  border-radius: var(--openexam-radius-md) !important;
}

.el-input__inner,
.el-textarea__inner {
  color: var(--openexam-text-primary) !important;
}

.el-input__inner::placeholder,
.el-textarea__inner::placeholder {
  color: var(--openexam-text-tertiary) !important;
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
  color: var(--openexam-text-primary) !important;
}

.el-dialog {
  background: var(--openexam-bg-primary) !important;
  border: 1px solid var(--openexam-border);
  border-radius: var(--openexam-radius-xl) !important;
  box-shadow: var(--openexam-shadow-lg) !important;
}

.el-dialog__header {
  padding: var(--openexam-space-6) var(--openexam-space-6) var(--openexam-space-3) !important;
}

.el-dialog__body {
  padding: var(--openexam-space-5) var(--openexam-space-6) var(--openexam-space-2) !important;
}

.el-dialog__footer {
  padding: var(--openexam-space-4) var(--openexam-space-6) var(--openexam-space-6) !important;
}

.el-dialog__title,
.el-drawer__title {
  color: var(--openexam-text-primary) !important;
  font-weight: var(--openexam-font-semibold);
  font-size: var(--openexam-font-lg);
}

.el-message {
  border-radius: var(--openexam-radius-md) !important;
  background: var(--openexam-bg-primary) !important;
  border: 1px solid var(--openexam-border) !important;
}

.el-button--primary {
  --el-button-bg-color: var(--openexam-primary) !important;
  --el-button-border-color: var(--openexam-primary) !important;
  --el-button-hover-bg-color: var(--openexam-primary-dark) !important;
  --el-button-hover-border-color: var(--openexam-primary-dark) !important;
  --el-button-active-bg-color: var(--openexam-primary-dark) !important;
  --el-button-active-border-color: var(--openexam-primary-dark) !important;
  --el-button-text-color: #ffffff !important;
  border-radius: var(--openexam-radius-full) !important;
  box-shadow: 0 4px 14px 0 rgba(59, 130, 246, 0.39);
}

.el-button:not(.el-button--primary) {
  background: var(--openexam-bg-primary);
  border-color: var(--openexam-border);
  color: var(--openexam-text-primary);
  border-radius: var(--openexam-radius-full);
}

.el-button {
  min-height: 36px;
  padding-inline: var(--openexam-space-4);
  font-weight: var(--openexam-font-medium);
}

.el-pagination {
  justify-content: flex-end;
  margin-top: var(--openexam-space-5);
}

.el-button--text,
.el-button.is-link {
  color: var(--openexam-primary) !important;
}

.el-select-dropdown,
.el-picker-panel,
.el-dropdown-menu,
.el-message-box {
  background: var(--openexam-bg-primary) !important;
  border-color: var(--openexam-border) !important;
  color: var(--openexam-text-primary) !important;
  border-radius: var(--openexam-radius-md) !important;
}

.el-message-box__title,
.el-message-box__message,
.el-select-dropdown__item,
.el-dropdown-menu__item {
  color: var(--openexam-text-primary) !important;
}

.el-empty__description p {
  color: var(--openexam-text-tertiary) !important;
}

.el-menu {
  border-right: none !important;
  background: var(--openexam-bg-primary) !important;
}

.el-menu-item {
  color: var(--openexam-text-primary) !important;
  height: 48px !important;
  line-height: 48px !important;
  margin: 0 var(--openexam-space-2) !important;
  border-radius: var(--openexam-radius-md) !important;
}

.el-menu-item.is-active {
  background-color: var(--openexam-primary-light) !important;
  color: var(--openexam-primary) !important;
}

.el-menu-item:hover {
  background-color: var(--openexam-bg-tertiary) !important;
}
</style>
