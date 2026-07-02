'use client'

import { useState, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { ArrowLeft, Upload, Loader2, Download, MessageSquare, CheckCircle, Image as ImageIcon } from 'lucide-react'
import JSZip from 'jszip'
import { saveAs } from 'file-saver'
import * as htmlToImage from 'html-to-image'

interface SlideData {
  title: string
  subtitle: string
  body?: string
  imagePrompt: string
  backgroundUrl?: string
}

interface ChatMessage {
  role: 'user' | 'model'
  text: string
}

export default function CarouselGeneratorPage() {
  const router = useRouter()
  // Settings
  const [topic, setTopic] = useState('')
  const [modelChoice, setModelChoice] = useState('presentation')
  const [aspectRatio, setAspectRatio] = useState('4:5')
  const [slideCount, setSlideCount] = useState(6)
  const [referenceImage, setReferenceImage] = useState<string | null>(null)

  // State
  const [phase, setPhase] = useState<'setup' | 'drafting' | 'finalized'>('setup')
  const [isGenerating, setIsGenerating] = useState(false)
  
  // Drafting Data
  const [draft, setDraft] = useState<SlideData[] | null>(null)
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([])
  const [userFeedback, setUserFeedback] = useState('')

  // Final Data
  const [slides, setSlides] = useState<SlideData[] | null>(null)
  const carouselRef = useRef<HTMLDivElement>(null)

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = (event) => {
      setReferenceImage(event.target?.result as string)
    }
    reader.readAsDataURL(file)
  }

  const handleGenerateDraft = async () => {
    if (!topic) return
    setIsGenerating(true)
    
    try {
      const res = await fetch('/api/draft-carousel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          topic, 
          slideCount, 
          referenceImage,
          chatHistory: [],
          currentDraft: null
        })
      })
      
      const data = await res.json()
      if (data.draft) {
        setDraft(data.draft)
        setPhase('drafting')
        setChatHistory([])
      }
    } catch (e) {
      console.error(e)
    } finally {
      setIsGenerating(false)
    }
  }

  const handleSendFeedback = async () => {
    if (!userFeedback.trim() || !draft) return
    setIsGenerating(true)
    
    const newHistory: ChatMessage[] = [
      ...chatHistory,
      { role: 'user', text: userFeedback }
    ]
    setChatHistory(newHistory)
    setUserFeedback('')
    
    try {
      const res = await fetch('/api/draft-carousel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          topic, 
          slideCount, 
          referenceImage,
          chatHistory: newHistory,
          currentDraft: draft
        })
      })
      
      const data = await res.json()
      if (data.draft) {
        setDraft(data.draft)
        setChatHistory([
          ...newHistory,
          { role: 'model', text: 'Я обновил черновик с учетом ваших правок. Посмотрите!' }
        ])
      }
    } catch (e) {
      console.error(e)
    } finally {
      setIsGenerating(false)
    }
  }

  const handleGenerateFinal = async () => {
    if (!draft) return
    setIsGenerating(true)
    
    try {
      // Check for Telegram WebApp environment
      const tg = (window as any).Telegram?.WebApp
      const telegramId = tg?.initDataUnsafe?.user?.id

      const res = await fetch('/api/generate-carousel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          slides: draft, 
          modelChoice,
          referenceImage,
          aspectRatio,
          telegramId
        })
      })
      
      const data = await res.json()
      if (data.slides) {
        setSlides(data.slides)
        setPhase('finalized')
      }
    } catch (e) {
      console.error(e)
    } finally {
      setIsGenerating(false)
    }
  }

  const [isSending, setIsSending] = useState(false)

  const sendToBot = async () => {
    if (!carouselRef.current || !slides) return
    setIsSending(true)
    
    // Check for Telegram WebApp environment
    const tg = (window as any).Telegram?.WebApp
    const chatId = tg?.initDataUnsafe?.user?.id
    
    const slideElements = carouselRef.current.querySelectorAll('.carousel-slide')
    const images: string[] = []
    
    for (let i = 0; i < slideElements.length; i++) {
      const element = slideElements[i] as HTMLElement
      try {
        const dataUrl = await htmlToImage.toPng(element, { quality: 1.0, pixelRatio: 2 })
        images.push(dataUrl)
      } catch (err) {
        console.error('Failed to render slide', i, err)
      }
    }

    try {
      if (chatId) {
        // We are inside Telegram Mini App, send via bot
        const res = await fetch('/api/bot/send-images', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ chatId, images, topic })
        })
        if (res.ok) {
          tg?.showAlert?.('Картинки успешно отправлены вам в чат!')
        } else {
          tg?.showAlert?.('Ошибка при отправке картинок.')
        }
      } else {
        // Fallback for desktop browser without Telegram context - just download them as a ZIP
        try {
          const zip = new JSZip()
          for (let i = 0; i < images.length; i++) {
            // Remove 'data:image/png;base64,' to get raw base64 data
            const base64Data = images[i].split(',')[1]
            zip.file(`slide_${i + 1}.png`, base64Data, { base64: true })
          }
          const content = await zip.generateAsync({ type: 'blob' })
          saveAs(content, 'carousel_slides.zip')
        } catch (zipError) {
          console.error('Failed to create ZIP', zipError)
          alert('Ошибка при архивации картинок.')
        }
      }
    } catch (e) {
      console.error(e)
    } finally {
      setIsSending(false)
    }
  }

  const getDimensions = () => {
    switch(aspectRatio) {
      case '1:1': return { w: 1080, h: 1080 }
      case '3:4': return { w: 1080, h: 1440 }
      case '4:5': return { w: 1080, h: 1350 }
      case '9:16': return { w: 1080, h: 1920 }
      case '16:9': return { w: 1920, h: 1080 }
      default: return { w: 1080, h: 1350 }
    }
  }

  const dims = getDimensions()

  return (
    <div className="max-w-2xl mx-auto p-4 pb-20">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <button 
          onClick={() => {
            if (phase === 'finalized') setPhase('drafting')
            else if (phase === 'drafting') setPhase('setup')
            else router.back()
          }}
          className="p-2 bg-white/5 rounded-full hover:bg-white/10 transition-colors"
        >
          <ArrowLeft className="w-5 h-5 text-gray-300" />
        </button>
        <div>
          <h1 className="text-xl font-bold">Контент Завод</h1>
          <p className="text-gray-400 text-xs">AI Карусели</p>
        </div>
      </div>

      {/* PHASE 1: SETUP */}
      {phase === 'setup' && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div className="glass-panel p-4 rounded-3xl border border-white/10">
              <label className="block text-sm font-semibold mb-2">Слайдов</label>
              <input 
                type="number" 
                min="2" max="10" 
                value={slideCount}
                onChange={(e) => setSlideCount(parseInt(e.target.value) || 6)}
                className="w-full bg-white/5 border border-white/20 rounded-xl p-3 text-white focus:outline-none focus:border-white/40 focus:ring-1 focus:ring-white/40 transition-colors"
              />
            </div>
            <div className="glass-panel p-4 rounded-3xl border border-white/10">
              <label className="block text-sm font-semibold mb-2">Формат</label>
              <select 
                value={aspectRatio}
                onChange={(e) => setAspectRatio(e.target.value)}
                className="w-full bg-black/40 border border-white/10 rounded-xl p-3 text-white focus:outline-none"
              >
                <option value="1:1">1:1 (Квадрат)</option>
                <option value="4:5">4:5 (Пост)</option>
                <option value="3:4">3:4 (Портрет)</option>
                <option value="9:16">9:16 (Stories/Reels)</option>
                <option value="16:9">16:9 (YouTube)</option>
              </select>
            </div>
          </div>

          {/* Image generation fields */}
          <div className="space-y-4 pt-4 border-t border-white/10">
            <h3 className="text-lg font-medium">Визуал</h3>
            
            <div className="space-y-2">
              <label className="text-sm text-gray-400">Референсное фото (опционально)</label>
            </div>
            <select 
              value={modelChoice}
              onChange={(e) => setModelChoice(e.target.value)}
              className="w-full bg-black/40 border border-white/10 rounded-xl p-3 text-white focus:outline-none"
            >
              <option value="presentation">Презентация (Без ИИ-фонов)</option>
              <option value="nano">Nano Banana (Быстрый ИИ-фон)</option>
              <option value="nano2">Nano 2 (Продвинутый ИИ-фон)</option>
            </select>
          </div>

          <div className="glass-panel p-6 rounded-3xl border border-white/10 text-center relative overflow-hidden">
            {referenceImage ? (
              <div className="absolute inset-0 z-0 opacity-40">
                <img src={referenceImage} alt="Reference" className="w-full h-full object-cover blur-sm" />
              </div>
            ) : null}
            <div className="relative z-10">
              <div className="w-16 h-16 bg-white/5 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-dashed border-white/20">
                {referenceImage ? <ImageIcon className="w-8 h-8 text-purple-400" /> : <Upload className="w-8 h-8 text-gray-400" />}
              </div>
              <h3 className="font-semibold mb-1">Референс Фото (Опционально)</h3>
              <p className="text-gray-400 text-xs mb-4">
                Загрузите фото, чтобы ИИ перенял его стиль
              </p>
              <button 
                onClick={() => document.getElementById('reference-upload')?.click()}
                className="cursor-pointer px-6 py-2 bg-white/10 hover:bg-white/20 rounded-full text-sm font-medium transition-colors inline-block"
              >
                Выбрать фото
              </button>
              <input id="reference-upload" type="file" accept="image/*" className="hidden" onChange={handleImageUpload} />
            </div>
          </div>

          <div className="glass-panel p-6 rounded-3xl border border-white/10">
            <label className="block font-semibold mb-2">О чем будет карусель?</label>
            <textarea 
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="Подробно опишите вашу идею..."
              className="w-full bg-black/40 border border-white/10 rounded-xl p-4 min-h-[100px] text-white focus:outline-none focus:border-purple-500/50 resize-none"
            />
          </div>

          <button 
            onClick={handleGenerateDraft}
            disabled={!topic || isGenerating}
            className="w-full py-4 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-600/50 disabled:cursor-not-allowed rounded-2xl font-bold text-white shadow-[0_0_30px_rgba(147,51,234,0.3)] transition-all flex items-center justify-center gap-2"
          >
            {isGenerating ? <><Loader2 className="w-5 h-5 animate-spin" /> Пишем сценарий...</> : <><MessageSquare className="w-5 h-5" /> Создать Черновик</>}
          </button>
        </div>
      )}

      {/* PHASE 2: DRAFTING */}
      {phase === 'drafting' && draft && (
        <div className="space-y-6">
          <div className="glass-panel p-6 rounded-3xl border border-white/10">
            <h2 className="text-xl font-bold mb-4">Черновик ({draft.length} слайдов)</h2>
            <div className="space-y-4">
              {draft.map((s, i) => (
                <div key={i} className="p-4 bg-white/5 rounded-xl border border-white/5 space-y-2">
                  <div className="text-xs text-purple-400 font-bold mb-1">{s.title}</div>
                  <div className="font-medium text-lg leading-snug">{s.subtitle}</div>
                  {s.body && (
                    <div className="text-sm text-gray-300 mt-2 p-3 bg-black/40 rounded-lg">
                      <span className="text-xs text-gray-500 uppercase tracking-widest block mb-1">Основной текст</span>
                      {s.body}
                    </div>
                  )}
                  {s.imagePrompt && (
                    <div className="text-xs text-blue-300/70 mt-2 p-3 bg-blue-900/20 border border-blue-500/20 rounded-lg">
                      <span className="text-xs text-blue-400/50 uppercase tracking-widest block mb-1">ТЗ для визуала (Prompt)</span>
                      {s.imagePrompt}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Chat History */}
          {chatHistory.length > 0 && (
            <div className="glass-panel p-6 rounded-3xl border border-white/10 space-y-4">
              {chatHistory.map((msg, i) => (
                <div key={i} className={`p-3 rounded-xl max-w-[85%] ${msg.role === 'user' ? 'bg-purple-600/30 ml-auto border border-purple-500/20' : 'bg-white/5 mr-auto border border-white/5'}`}>
                  <p className="text-sm">{msg.text}</p>
                </div>
              ))}
            </div>
          )}

          {/* Feedback Input */}
          <div className="flex gap-2">
            <input 
              type="text" 
              value={userFeedback}
              onChange={(e) => setUserFeedback(e.target.value)}
              placeholder="Что исправить? (напр: сделай жестче)"
              onKeyDown={(e) => e.key === 'Enter' && handleSendFeedback()}
              className="flex-1 bg-black/40 border border-white/10 rounded-xl p-3 text-white focus:outline-none"
            />
            <button 
              onClick={handleSendFeedback}
              disabled={isGenerating || !userFeedback.trim()}
              className="px-4 bg-white/10 hover:bg-white/20 disabled:opacity-50 rounded-xl transition-colors"
            >
              {isGenerating ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Отправить'}
            </button>
          </div>

          <button 
            onClick={handleGenerateFinal}
            disabled={isGenerating}
            className="w-full py-4 bg-green-600 hover:bg-green-700 disabled:bg-green-600/50 rounded-2xl font-bold text-white shadow-[0_0_30px_rgba(22,163,74,0.3)] transition-all flex items-center justify-center gap-2 mt-4"
          >
            {isGenerating ? <><Loader2 className="w-5 h-5 animate-spin" /> Генерируем дизайн...</> : <><CheckCircle className="w-5 h-5" /> Одобрить и создать дизайн</>}
          </button>
        </div>
      )}

      {/* PHASE 3: FINALIZED */}
      {phase === 'finalized' && slides && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-lg">Готово! 🎉</h3>
            <button 
              onClick={() => { setPhase('setup'); setDraft(null); setSlides(null); }}
              className="text-sm text-purple-400 hover:text-purple-300"
            >
              Сделать еще
            </button>
          </div>
          
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
                    width: `${dims.w}px`, 
                    height: `${dims.h}px`,
                    transform: 'scale(0.25)', 
                    transformOrigin: 'top left',
                    marginBottom: `-${dims.h * 0.75}px`,
                    marginRight: `-${dims.w * 0.75}px`,
                    backgroundColor: '#111'
                  }}
                >
                  <div 
                    className="absolute inset-0 z-0"
                    style={{
                      backgroundImage: "url('" + slide.backgroundUrl + "')",
                      backgroundSize: 'cover',
                      backgroundPosition: 'center',
                      opacity: 0.6
                    }}
                  />
                  <div className="absolute inset-0 z-10 bg-gradient-to-t from-black/80 via-black/40 to-transparent" />

                  <div className="relative z-20 flex flex-col items-center gap-8 text-white w-full px-8 mt-auto mb-32">
                    <div className="px-6 py-2 bg-purple-600/80 backdrop-blur-md rounded-full text-3xl font-bold tracking-widest uppercase border border-white/20 shadow-xl">
                      {slide.title}
                    </div>
                    <h2 className="text-7xl font-black leading-tight text-shadow-xl" style={{ textShadow: '0 10px 30px rgba(0,0,0,0.8)' }}>
                      {slide.subtitle}
                    </h2>
                  </div>

                  <div className="absolute top-12 left-12 z-20 text-white/50 text-3xl font-mono">
                    0{i + 1}
                  </div>
                  <div className="absolute bottom-12 z-20 text-white/50 text-2xl font-bold flex items-center gap-4">
                    <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
                       <span className="text-white">AI</span>
                    </div>
                    @n8_assistant_bot
                  </div>
                </div>
              ))}
            </div>
          </div>

          <button 
            onClick={sendToBot}
            disabled={isSending}
            className="w-full py-4 bg-white text-black hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed rounded-2xl font-bold transition-all flex items-center justify-center gap-2 mt-8"
          >
            {isSending ? <Loader2 className="w-5 h-5 animate-spin" /> : <MessageSquare className="w-5 h-5" />}
            {isSending ? 'Отправляем...' : `Отправить ${slides.length} слайдов в чат`}
          </button>
        </div>
      )}
    </div>
  )
}
