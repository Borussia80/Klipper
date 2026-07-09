export default defineNuxtPlugin(async () => {
  const { token } = useApi()
  const { user, fetchCurrentUser } = useAuth()

  if (token.value && !user.value) {
    try {
      await fetchCurrentUser()
    } catch {
      // useApi's onResponseError already clears the token and redirects
      // on a 401; any other failure just leaves the session unhydrated.
    }
  }
})
