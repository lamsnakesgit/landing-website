'use client'

import { useState, useRef } from 'react'
import { ArrowLeft, Upload, Loader2, ImageIcon, Sparkles, Download } from 'lucide-react'
import Link from 'next/link'
import * as htmlToImage from 'html-to-image'

interface SlideData {
  title: string
  subtitle: string
  backgroundUrl: string
}

export default function CarouselGeneratorPage() {
  const [topic, setTopic] = useState('')
  const [modelChoice, setModelChoice] = useState('nano')
  const [isGenerating, setIsGenerating] = useState(false)
  const [slides, setSlides] = useState<SlideData[] | null>(null)
  const carouselRef = useRef<HTMLDivElement>(null)

  const handleGenerate = async () => {
    if (!topic) return
    setIsGenerating(true)
    
    try {
      const res = await fetch('/api/generate-carousel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, modelChoice })
      })
      
      const data = await res.json()
      if (data.slides) {
        setSlides(data.slides)
      }
    } catch (e) {
      console.error(e)
    } finally {
      setIsGenerating(false)
    }
  }

  const downloadAll = async () => {
    if (!carouselRef.current || !slides) return
    
    const slideElements = carouselRef.current.querySelectorAll('.carousel-slide')
    
    for (let i = 0; i < slideElements.length; i++) {
      const element = slideElements[i] as HTMLElement
      try {
        const dataUrl = await htmlToImage.toPng(element, { quality: 1.0, pixelRatio: 2 })
        const link = document.createElement('a')
        link.download = `slide_${i + 1}.png`
        link.href = dataUrl
        link.click()
        // Небольшая пауза чтобы браузер успел скачать
        await new Promise(r => setTimeout(r, 300))
      } catch (err) {
        console.error('Failed to download slide', i, err)
      }
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
          <p className="text-gray-400 text-xs">AI Карусели 4:5</p>
        </div>
      </div>

      {!slides ? (
        <div className="space-y-6">
          {/* Reference Image Upload */}
          <div className="glass-panel p-6 rounded-3xl border border-white/10 text-center">
            <div className="w-16 h-16 bg-white/5 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-dashed border-white/20">
              <Upload className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="font-semibold mb-1">Референс Лица</h3>
            <p className="text-gray-400 text-xs mb-4">
              Ваше лицо будет встроено в фон
            </p>
            <button className="px-6 py-2 bg-white/10 hover:bg-white/20 rounded-full text-sm font-medium transition-colors">
              Выбрать фото
            </button>
          </div>

          {/* Model Selection */}
          <div className="glass-panel p-4 rounded-3xl border border-white/10">
            <label className="block text-sm font-semibold mb-2">Нейросеть (Vertex AI / GRSai)</label>
            <select 
              value={modelChoice}
              onChange={(e) => setModelChoice(e.target.value)}
              className="w-full bg-black/40 border border-white/10 rounded-xl p-3 text-white focus:outline-none"
            >
              <option value="nano">Nano Banana (gemini-3.1-flash)</option>
              <option value="nano2">Nano Banana Pro (gemini-3-pro)</option>
            </select>
          </div>

          {/* Topic Input */}
          <div className="glass-panel p-6 rounded-3xl border border-white/10">
            <label className="block font-semibold mb-2">О чем пост?</label>
            <textarea 
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="Как продавать через ИИ-агентов..."
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
                Создаем дизайн и текст...
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                Сгенерировать Карусель
              </>
            )}
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-lg">Готово! 🎉</h3>
            <button 
              onClick={() => setSlides(null)}
              className="text-sm text-purple-400 hover:text-purple-300"
            >
              Сделать еще
            </button>
          </div>
          
          {/* Скрытый контейнер для рендеринга 1080x1350 */}
          {/* Мы показываем уменьшенную копию через CSS scale, но рендерим в оригинальном размере */}
          <div className="overflow-x-auto pb-4 hide-scrollbar">
            <div 
              ref={carouselRef}
              className="flex gap-4 w-max"
            >
              {slides.map((slide, i) => (
                <div 
                  key={i} 
                  className="carousel-slide relative overflow-hidden flex flex-col justify-center items-center text-center p-12"
                  style={{ 
                    width: '1080px', 
                    height: '1350px',
                    transform: 'scale(0.25)', // Уменьшаем для предпросмотра
                    transformOrigin: 'top left',
                    marginBottom: '-1012px', // Компенсируем высоту scale
                    marginRight: '-810px', // Компенсируем ширину scale
                    backgroundColor: '#111'
                  }}
                >
                  {/* Фоновая картинка сграбленная с AI */}
                  <div 
                    className="absolute inset-0 z-0"
                    style={{
                      backgroundImage: \`url('\${slide.backgroundUrl}')\`,
                      backgroundSize: 'cover',
                      backgroundPosition: 'center',
                      opacity: 0.6
                    }}
                  />
                  
                  {/* Темный градиент для читаемости текста */}
                  <div className="absolute inset-0 z-10 bg-gradient-to-t from-black/80 via-black/40 to-transparent" />

                  {/* Контент поверх фона */}
                  <div className="relative z-20 flex flex-col items-center gap-8 text-white w-full px-8 mt-auto mb-32">
                    <div className="px-6 py-2 bg-purple-600/80 backdrop-blur-md rounded-full text-3xl font-bold tracking-widest uppercase border border-white/20 shadow-xl">
                      {slide.title}
                    </div>
                    <h2 className="text-7xl font-black leading-tight text-shadow-xl" style={{ textShadow: '0 10px 30px rgba(0,0,0,0.8)' }}>
                      {slide.subtitle}
                    </h2>
                  </div>

                  {/* Декоративные элементы */}
                  <div className="absolute top-12 left-12 z-20 text-white/50 text-3xl font-mono">
                    0{i + 1}
                  </div>
                  <div className="absolute bottom-12 z-20 text-white/50 text-2xl font-bold flex items-center gap-4">
                    <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
                       <span className="text-white">AI</span>
                    </div>
                    @ai_assistant
                  </div>
                </div>
              ))}
            </div>
          </div>

          <button 
            onClick={downloadAll}
            className="w-full py-4 bg-white text-black hover:bg-gray-200 rounded-2xl font-bold transition-all flex items-center justify-center gap-2 mt-8"
          >
            <Download className="w-5 h-5" />
            Скачать 6 слайдов (PNG)
          </button>
        </div>
      )}
    </div>
  )
}
