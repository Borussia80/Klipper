import { defaultCache } from "@serwist/next/worker"
import { Serwist } from "serwist"

// __SW_MANIFEST é injetado pelo Serwist no build; `any` evita conflito dom/webworker
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const swSelf = self as any

const serwist = new Serwist({
  // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
  precacheEntries: swSelf.__SW_MANIFEST,
  skipWaiting: true,
  clientsClaim: true,
  navigationPreload: true,
  runtimeCaching: defaultCache,
})

serwist.addEventListeners()
