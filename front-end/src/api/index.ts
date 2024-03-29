import type { AxiosProgressEvent, GenericAbortSignal } from 'axios'
import { post } from '@/utils/request'

// export function fetchChatAPI<T = any>(
//   prompt: string,
//   options?: { conversationId?: string; parentMessageId?: string },
//   signal?: GenericAbortSignal,
// ) {
//   return post<T>({
//     url: '/chat',
//     data: { prompt, options },
//     signal,
//   })
// }

// export function fetchChatConfig<T = any>() {
//   return post<T>({
//     url: '/config',
//   })
// }

export function fetchChatAPIProcess<T = any>(
  params: {
    prompt: string
    options?: { conversationId?: string; parentMessageId?: string }
    signal?: GenericAbortSignal
    onDownloadProgress?: (progressEvent: AxiosProgressEvent) => void },
) {
  return post<T>({
    url: '/chat-process',
    data: { prompt: params.prompt, options: params.options },
    signal: params.signal,
    onDownloadProgress: params.onDownloadProgress,
  })
}

// 获取对应文本语音
export function fetchVoice( text: string ) {
  return post({
    url: 'http://127.0.0.1:7860/run/predict',
    data: {
      "fn_index": 0,
      "data": [
        text,
        "scaramouche",
        "简体中文",
        1
      ],
      "session_hash": "iribhymowma123"
    }
  })
}

// export function fetchSession<T>() {
//   return post<T>({
//     url: '/session',
//   })
// }

// export function fetchVerify<T>(token: string) {
//   return post<T>({
//     url: '/verify',
//     data: { token },
//   })
// }