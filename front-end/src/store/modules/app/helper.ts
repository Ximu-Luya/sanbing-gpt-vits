import { ss } from '@/utils/storage'

const LOCAL_NAME = 'appSetting'

export type Theme = 'light' | 'dark' | 'auto'

export type Language = 'zh-CN' | 'zh-TW' | 'en-US'

export interface AppState {
  siderCollapsed: boolean
  chatDataViewerCollapsed: boolean
  chatDataLoading: boolean
  theme: Theme
  language: Language
  voiceEngineAvailable: boolean // 本地AI音频引擎服务是否可用
}

export function defaultSetting(): AppState {
  return { 
    siderCollapsed: false,
    chatDataViewerCollapsed: false,
    chatDataLoading: false,
    theme: 'light',
    language: 'zh-CN',
    voiceEngineAvailable: true // 默认可用
  }
}

export function getLocalSetting(): AppState {
  const localSetting: AppState | undefined = ss.get(LOCAL_NAME)
  return { ...defaultSetting(), ...localSetting }
}

export function setLocalSetting(setting: AppState): void {
  ss.set(LOCAL_NAME, setting)
}
