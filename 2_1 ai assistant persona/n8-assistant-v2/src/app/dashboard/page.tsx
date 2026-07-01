'use client'

import { useEffect, useState } from 'react'
import { ArrowRight, ImageIcon, Settings, PlayCircle, Loader2 } from 'lucide-react'
import Link from 'next/link'

interface TgUser {
  id: number
  first_name: string
  last_name?: string
  username?: string
}

export default function MiniAppDashboard() {
  const [tgUser, setTgUser] = useState<TgUser | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check if we are inside Telegram Web App
    if (typeof window !== 'undefined' && (window as any).Telegram?.WebApp) {
      const tg = (window as any).Telegram.WebApp
      tg.ready() // tell TG the app is ready
      tg.expand() // expand to full height
      
      const user = tg.initDataUnsafe?.user
      if (user) {
        setTgUser(user)
      } else {
        // Mock user for local browser testing
        setTgUser({
          id: 123456789,
          first_name: 'Тестер',
          username: 'tester'
        })
      }
    } else {
      // Mock for local testing outside TG
      setTgUser({
        id: 123456789,
        first_name: 'Локальный',
        username: 'local'
      })
    }
    setIsLoading(false)
  }, [])

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    )
  }

  return (
    <div className="max-w-md mx-auto p-4 pb-20">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold">Привет, {tgUser?.first_name}! 👋</h1>
          <p className="text-gray-400 text-sm">Твой AI-ассистент готов</p>
        </div>
        <div className="bg-blue-500/20 text-blue-400 px-3 py-1.5 rounded-full text-sm font-bold border border-blue-500/30">
          3 💎
        </div>
      </div>

      {/* Video Pitch / Onboarding Circle Placeholder */}
      <div className="mb-10 flex flex-col items-center justify-center text-center">
        <div className="relative w-48 h-48 rounded-full overflow-hidden border-4 border-blue-500/30 mb-4 bg-gray-900 flex items-center justify-center shadow-[0_0_30px_rgba(59,130,246,0.3)]">
          {/* Here we will put the actual video tag later */}
          <PlayCircle className="w-16 h-16 text-gray-500" />
          <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
            <span className="text-sm font-medium">Смотреть питч</span>
          </div>
        </div>
        <h2 className="text-xl font-semibold mb-1">Добро пожаловать!</h2>
        <p className="text-gray-400 text-sm max-w-[250px]">
          Посмотрите короткое видео о том, как работает наш ИИ-контент завод.
        </p>
      </div>

      {/* Main Features */}
      <div className="flex flex-col gap-4">
        {/* Content Factory */}
        <Link 
          href="/dashboard/carousel-generator"
          className="glass-panel p-6 rounded-3xl relative overflow-hidden group border border-purple-500/30 hover:border-purple-500/60 transition-all flex items-center gap-4"
        >
          <div className="w-12 h-12 bg-purple-500/20 rounded-xl flex items-center justify-center shrink-0">
            <ImageIcon className="w-6 h-6 text-purple-400" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-bold mb-1">Мини Контент Завод</h3>
            <p className="text-gray-400 text-xs">
              Генерация каруселей по вашим референсам
            </p>
          </div>
          <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-white transition-colors" />
        </Link>

        {/* Calendar / Integrations placeholder */}
        <Link 
          href="/dashboard/integrations"
          className="glass-panel p-6 rounded-3xl relative overflow-hidden group border border-white/10 hover:border-white/20 transition-all flex items-center gap-4 opacity-70 hover:opacity-100"
        >
          <div className="w-12 h-12 bg-white/10 rounded-xl flex items-center justify-center shrink-0">
            <Settings className="w-6 h-6 text-gray-400" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-bold mb-1">Интеграции</h3>
            <p className="text-gray-400 text-xs">
              Google Календарь, Диск, Notion
            </p>
          </div>
          <ArrowRight className="w-5 h-5 text-gray-400 transition-colors" />
        </Link>
      </div>
    </div>
  )
}
