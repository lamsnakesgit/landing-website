'use client'

import { useEffect, useState } from 'react'
import { ArrowLeft, Calendar, FileText, LayoutList, Loader2 } from 'lucide-react'
import Link from 'next/link'
import { connectNango } from './actions'
import { startTransition } from 'react'
interface TgUser {
  id: number
  first_name: string
  username?: string
}

export default function IntegrationsPage() {
  const [tgUser, setTgUser] = useState<TgUser | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (typeof window !== 'undefined' && (window as any).Telegram?.WebApp) {
      const tg = (window as any).Telegram.WebApp
      tg.ready()
      const user = tg.initDataUnsafe?.user
      if (user) {
        setTgUser(user)
      } else {
        setTgUser({ id: 123456789, first_name: 'Тестер', username: 'tester' })
      }
    } else {
      setTgUser({ id: 123456789, first_name: 'Локальный', username: 'local' })
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

  const handleConnect = (provider: string) => {
    const chatId = tgUser?.id || 'unknown';
    startTransition(() => {
      connectNango(provider, String(chatId));
    });
  };

  const integrations = [
    {
      id: 'google-calendar',
      name: 'Google Календарь',
      description: 'Доступ к расписанию и встречам',
      icon: <Calendar className="w-6 h-6 text-blue-400" />,
      color: 'bg-blue-500/20 border-blue-500/30'
    },
    {
      id: 'google-docs',
      name: 'Google Docs',
      description: 'Чтение и создание документов',
      icon: <FileText className="w-6 h-6 text-blue-400" />,
      color: 'bg-blue-500/20 border-blue-500/30'
    },
    {
      id: 'notion',
      name: 'Notion',
      description: 'Подключение к базам данных Notion',
      icon: <LayoutList className="w-6 h-6 text-gray-200" />,
      color: 'bg-white/10 border-white/20'
    }
  ];

  return (
    <div className="max-w-md mx-auto p-4 pb-20 relative z-10">
      <div className="flex items-center gap-4 mb-8">
        <Link href="/dashboard" className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center hover:bg-white/10 transition-colors">
          <ArrowLeft className="w-5 h-5 text-gray-400" />
        </Link>
        <h1 className="text-2xl font-bold">Интеграции</h1>
      </div>

      <p className="text-gray-400 text-sm mb-6">
        Подключите ваши любимые сервисы, чтобы AI-ассистент мог читать и создавать документы, а также управлять вашим расписанием.
      </p>

      <div className="flex flex-col gap-4">
        {integrations.map((integration) => (
          <button
            key={integration.id}
            onClick={() => handleConnect(integration.id)}
            className={`glass-panel p-5 rounded-2xl flex items-center gap-4 border hover:opacity-80 transition-opacity ${integration.color} text-left w-full`}
          >
            <div className="w-12 h-12 rounded-xl flex items-center justify-center shrink-0 bg-black/20">
              {integration.icon}
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-bold mb-1">{integration.name}</h3>
              <p className="text-gray-400 text-xs">{integration.description}</p>
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}
