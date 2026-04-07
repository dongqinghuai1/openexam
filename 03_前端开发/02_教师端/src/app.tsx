<template>
  <view class="app">
    <slot />
  </view>
</template>

<script setup>
import { onLaunch } from '@tarojs/taro'

onLaunch(() => {
  console.log('App launched.')
})
</script>

<style>
page {
  background-color: #f5f5f5;
}

.app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
}
</style>