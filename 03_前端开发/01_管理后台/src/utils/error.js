export function extractErrorMessage(error, fallback = '请求失败，请稍后重试') {
  const data = error?.response?.data
  if (!data) return fallback

  if (typeof data === 'string') return data
  if (data.error) return data.error
  if (data.detail) return data.detail
  if (data.message) return data.message

  const firstKey = Object.keys(data)[0]
  const firstValue = firstKey ? data[firstKey] : null

  if (Array.isArray(firstValue) && firstValue.length > 0) {
    return `${firstKey}: ${firstValue[0]}`
  }

  if (typeof firstValue === 'string') {
    return `${firstKey}: ${firstValue}`
  }

  return fallback
}
