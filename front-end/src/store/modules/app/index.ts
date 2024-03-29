import { defineStore } from 'pinia'
import type { AppState, Language, Theme } from './helper'
import { getLocalSetting, setLocalSetting } from './helper'
import { store } from '@/store'

export const useAppStore = defineStore('app-store', {
  state: (): AppState => getLocalSetting(),
  actions: {
    setSiderCollapsed(collapsed: boolean) {
      this.siderCollapsed = collapsed
      this.recordState()
    },

    setChatDataViewerCollapsed(collapsed: boolean) {
      this.chatDataViewerCollapsed = collapsed
      this.recordState()
    },

    setChatDataLoading(isLoading: boolean) {
      this.chatDataLoading = isLoading
      this.recordState()
    },

    // 设置AI音频服务可用性
    setVoiceEngineAvailable(available: boolean) {
      this.voiceEngineAvailable = available
      this.recordState()
    },

    setTheme(theme: Theme) {
      this.theme = theme
      this.recordState()
    },

    setLanguage(language: Language) {
      if (this.language !== language) {
        this.language = language
        this.recordState()
      }
    },

    recordState() {
      setLocalSetting(this.$state)
    },
  },
})

export function useAppStoreWithOut() {
  return useAppStore(store)
}
