import { reactive } from 'vue'

const toasts = reactive([])
let nextId = 0

function add(message, type = 'success', duration = 3500) {
  const id = ++nextId
  toasts.push({ id, message, type })
  setTimeout(() => remove(id), duration)
}

function remove(id) {
  const i = toasts.findIndex(t => t.id === id)
  if (i !== -1) toasts.splice(i, 1)
}

export function useToast() {
  return {
    toasts,
    remove,
    success: (msg) => add(msg, 'success'),
    error:   (msg) => add(msg, 'error'),
    info:    (msg) => add(msg, 'info'),
  }
}
