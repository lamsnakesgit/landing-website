import { Bot, Calendar, CreditCard, LayoutDashboard, MessageSquare, Settings } from "lucide-react";
import Link from "next/link";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-black text-white flex">
      {/* Sidebar */}
      <aside className="w-64 border-r border-white/10 glass-panel flex flex-col hidden md:flex">
        <div className="h-16 flex items-center px-6 border-b border-white/10">
          <Link href="/" className="flex items-center gap-2 font-bold text-lg">
            <Bot className="w-5 h-5 text-blue-500" />
            <span>AI Hands Assistant</span>
          </Link>
        </div>
        
        <nav className="flex-1 p-4 space-y-2">
          <Link href="/dashboard" className="flex items-center gap-3 px-4 py-3 rounded-xl bg-white/5 text-blue-400 font-medium">
            <LayoutDashboard className="w-5 h-5" />
            Главная
          </Link>
          <Link href="/dashboard/chat" className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/5 text-gray-400 hover:text-white transition-colors">
            <MessageSquare className="w-5 h-5" />
            AI Чат
          </Link>
          <Link href="/dashboard/calendar" className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/5 text-gray-400 hover:text-white transition-colors">
            <Calendar className="w-5 h-5" />
            Календарь
          </Link>
          <Link href="/dashboard/billing" className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/5 text-gray-400 hover:text-white transition-colors">
            <CreditCard className="w-5 h-5" />
            Кредиты
          </Link>
        </nav>

        <div className="p-4 border-t border-white/10">
          <Link href="/dashboard/settings" className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/5 text-gray-400 hover:text-white transition-colors">
            <Settings className="w-5 h-5" />
            Настройки
          </Link>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden relative">
        {/* Mobile Header */}
        <header className="h-16 border-b border-white/10 flex items-center px-6 md:hidden glass-panel z-10">
          <Bot className="w-5 h-5 text-blue-500 mr-2" />
          <span className="font-bold">AI Hands</span>
        </header>
        
        {/* Content Scroll Area */}
        <div className="flex-1 overflow-y-auto p-6 md:p-8 relative z-10">
          {children}
        </div>

        {/* Ambient background for dashboard */}
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-blue-900/20 blur-[120px] rounded-full pointer-events-none z-0" />
      </main>
    </div>
  );
}
