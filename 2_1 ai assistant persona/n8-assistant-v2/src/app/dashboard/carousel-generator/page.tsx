'use client'

import { useState } from 'react'
import { ArrowLeft, Upload, Loader2, ImageIcon, Sparkles } from 'lucide-react'
import Link from 'next/link'

export default function CarouselGeneratorPage() {
  const [topic, setTopic] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [result, setResult] = useState<string[] | null>(null)

  const handleGenerate = async () => {
    if (!topic) return
    setIsGenerating(true)
    
    try {
      // Mock API call
      await new Promise(r => setTimeout(r, 3000))
      setResult([
        'https://placehold.co/1080x1350/1e1e2e/ffffff?text=Slide+1:+Hook',
        'https://placehold.co/1080x1350/1e1e2e/ffffff?text=Slide+2:+Pain',
        'https://placehold.co/1080x1350/1e1e2e/ffffff?text=Slide+3:+Deep+Pain',
        'https://placehold.co/1080x1350/1e1e2e/ffffff?text=Slide+4:+Solution',
        'https://placehold.co/1080x1350/1e1e2e/ffffff?text=Slide+5:+Value',
        'https://placehold.co/1080x1350/1e1e2e/ffffff?text=Slide+6:+CTA',
      ])
    } catch (e) {
      console.error(e)
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="max-w-md mx-auto p-4 pb-20">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <Link href="/dashboard" className="p-2 bg-white/5 rounded-full hover:bg-white/10 transition-colors">
          <ArrowLeft className="w-5 h-5 text-gray-300" />
        </Link>
        <div>
          <h1 className="text-xl font-bold">Контент Завод</h1>
          <p className="text-gray-400 text-xs">Генерация карусели 4:5</p>
        </div>
      </div>

      {!result ? (
        <div className="space-y-6">
          {/* Reference Image Upload */}
          <div className="glass-panel p-6 rounded-3xl border border-white/10 text-center">
            <div className="w-16 h-16 bg-white/5 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-dashed border-white/20">
              <Upload className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="font-semibold mb-1">Загрузить Референс</h3>
            <p className="text-gray-400 text-xs mb-4">
              Фото вашего лица (необязательно)
            </p>
            <button className="px-6 py-2 bg-white/10 hover:bg-white/20 rounded-full text-sm font-medium transition-colors">
              Выбрать фото
            </button>
          </div>

          {/* Topic Input */}
          <div className="glass-panel p-6 rounded-3xl border border-white/10">
            <label className="block font-semibold mb-2">О чем будет карусель?</label>
            <textarea 
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="Например: Как использовать ИИ для продаж в Telegram..."
              className="w-full bg-black/40 border border-white/10 rounded-xl p-4 min-h-[100px] text-white focus:outline-none focus:border-purple-500/50 resize-none"
            />
          </div>

          {/* Generate Button */}
          <button 
            onClick={handleGenerate}
            disabled={!topic || isGenerating}
            className="w-full py-4 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-600/50 disabled:cursor-not-allowed rounded-2xl font-bold text-white shadow-[0_0_30px_rgba(147,51,234,0.3)] transition-all flex items-center justify-center gap-2"
          >
            {isGenerating ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Создаем 6 слайдов...
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                Сгенерировать (1 💎)
              </>
            )}
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Results View */}
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-lg">Готово! 🎉</h3>
            <button 
              onClick={() => setResult(null)}
              className="text-sm text-purple-400 hover:text-purple-300"
            >
              Сделать еще
            </button>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            {result.map((url, i) => (
              <div key={i} className="aspect-[4/5] bg-gray-900 rounded-xl overflow-hidden relative border border-white/10">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={url} alt={`Slide ${i+1}`} className="w-full h-full object-cover" />
                <div className="absolute top-2 left-2 bg-black/60 px-2 py-1 rounded text-xs font-mono">
                  {i + 1}/6
                </div>
              </div>
            ))}
          </div>

          <button className="w-full py-4 bg-white text-black hover:bg-gray-200 rounded-2xl font-bold transition-all flex items-center justify-center gap-2">
            <ImageIcon className="w-5 h-5" />
            Скачать все слайды
          </button>
        </div>
      )}
    </div>
  )
}
