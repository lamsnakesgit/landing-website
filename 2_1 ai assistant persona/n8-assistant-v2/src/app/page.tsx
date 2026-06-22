import { ArrowRight, Bot, Calendar, Image as ImageIcon, MessageSquare } from "lucide-react";
import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-black text-white selection:bg-blue-500/30 overflow-hidden relative">
      {/* Background gradients */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-blue-600/30 blur-[120px] rounded-full mix-blend-screen pointer-events-none" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-purple-600/30 blur-[120px] rounded-full mix-blend-screen pointer-events-none" />

      {/* Header */}
      <header className="fixed top-0 w-full z-50 glass-panel border-b border-white/5">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 font-bold text-xl tracking-tight">
            <Bot className="w-6 h-6 text-blue-500" />
            <span>N8 Assistant</span>
          </div>
          <Link
            href="/dashboard"
            className="px-4 py-2 bg-white text-black text-sm font-medium rounded-full hover:bg-gray-200 transition-colors"
          >
            Войти через Telegram
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <main className="relative pt-32 pb-16 sm:pt-40 sm:pb-24 lg:pb-32 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-5xl sm:text-7xl font-bold tracking-tight mb-8">
            Твой личный AI-сотрудник. <br className="hidden sm:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
              Работает 24/7.
            </span>
          </h1>
          <p className="mt-6 text-lg sm:text-xl text-gray-400 max-w-2xl mx-auto mb-10">
            Делегируй рутину. Мы создали платформу, где AI не просто общается, а ставит встречи в календарь, генерирует карусели и ведет переписку в WhatsApp.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/dashboard"
              className="group flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-full transition-all"
            >
              Попробовать бесплатно
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              href="#features"
              className="px-6 py-3 bg-white/5 hover:bg-white/10 text-white font-medium rounded-full transition-all border border-white/10"
            >
              Узнать больше
            </Link>
          </div>
        </div>

        {/* Feature Cards */}
        <div id="features" className="max-w-7xl mx-auto mt-32 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="glass-panel p-8 rounded-3xl relative overflow-hidden group hover:border-blue-500/50 transition-colors">
            <div className="w-12 h-12 bg-blue-500/20 rounded-2xl flex items-center justify-center mb-6">
              <Calendar className="w-6 h-6 text-blue-400" />
            </div>
            <h3 className="text-xl font-semibold mb-3">AI Секретарь</h3>
            <p className="text-gray-400">
              Автоматически планирует встречи, управляет Google Календарем и Notion через Maton MCP.
            </p>
          </div>

          <div className="glass-panel p-8 rounded-3xl relative overflow-hidden group hover:border-purple-500/50 transition-colors">
            <div className="w-12 h-12 bg-purple-500/20 rounded-2xl flex items-center justify-center mb-6">
              <ImageIcon className="w-6 h-6 text-purple-400" />
            </div>
            <h3 className="text-xl font-semibold mb-3">Контент Завод</h3>
            <p className="text-gray-400">
              Генерация готовых каруселей для Instagram и фотосессий через Nano Banana 2.
            </p>
          </div>

          <div className="glass-panel p-8 rounded-3xl relative overflow-hidden group hover:border-green-500/50 transition-colors">
            <div className="w-12 h-12 bg-green-500/20 rounded-2xl flex items-center justify-center mb-6">
              <MessageSquare className="w-6 h-6 text-green-400" />
            </div>
            <h3 className="text-xl font-semibold mb-3">WhatsApp Рассылки</h3>
            <p className="text-gray-400">
              Интеграция с твоим номером через Evolution API. Автоответы и прогрев лидов.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
