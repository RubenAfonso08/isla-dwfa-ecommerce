// `useFetch<T>` — os três estados (loading · error · data), escritos uma vez.
// The three states, written once; every screen that loads something reuses it.

import { ref, watchEffect, type Ref } from 'vue'
import { ApiError } from '@/api/client'

export type Status = 'idle' | 'loading' | 'error' | 'ok'

export function useFetch<T>(load: () => Promise<T>) {
  const data = ref<T | null>(null) as Ref<T | null>
  const status = ref<Status>('idle')
  const error = ref<string | null>(null)

  async function run() {
    status.value = 'loading'
    error.value = null
    try {
      data.value = await load()
      status.value = 'ok'
    } catch (e) {
      status.value = 'error'
      error.value = e instanceof ApiError ? e.message : 'Network error'
    }
  }

  // corre agora e sempre que uma dependência reativa de `load` mudar
  // runs now, and again whenever a reactive dependency read inside `load` changes
  watchEffect(() => {
    void run()
  })

  return { data, status, error, reload: run }
}
