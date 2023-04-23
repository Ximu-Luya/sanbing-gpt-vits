<script setup lang="ts">
import { NConfigProvider, NWatermark } from 'naive-ui'
import { NaiveProvider } from '@/components/common'
import { useTheme } from '@/hooks/useTheme'
import { useLanguage } from '@/hooks/useLanguage'

const { theme, themeOverrides } = useTheme()
const { language } = useLanguage()
</script>

<template>
  <NConfigProvider
    class="h-full"
    :theme="theme"
    :theme-overrides="themeOverrides"
    :locale="language"
  >
    <NaiveProvider>
      <RouterView />
    </NaiveProvider>
  </NConfigProvider>
  <NWatermark
    content="西木工作室"
    cross
    fullscreen
    :font-size="12"
    :line-height="12"
    :width="384"
    :height="384"
    :x-offset="12"
    :y-offset="60"
    :rotate="-15"
    :font-color="'rgba(128, 128, 128, .2)'"
  />
</template>
