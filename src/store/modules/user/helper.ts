import { ss } from '@/utils/storage'

const LOCAL_NAME = 'userStorage'

export interface RiderInfo {
  rider_id: number
  wb_list: any[]
}

export interface UserInfo {
  avatar: string
  name: string
  description: string
  riderInfo: RiderInfo
}

export interface UserState {
  userInfo: UserInfo
}

export function defaultSetting(): UserState {
  return {
    userInfo: {
      avatar: '/assets/rider_icon.png',
      name: '数字智能组',
      description: '决策智能中心',
      riderInfo: {}
    },
  }
}

export function getLocalState(): UserState {
  const localSetting: UserState | undefined = ss.get(LOCAL_NAME)
  return { ...defaultSetting(), ...localSetting }
}

export function setLocalState(setting: UserState): void {
  ss.set(LOCAL_NAME, setting)
}
