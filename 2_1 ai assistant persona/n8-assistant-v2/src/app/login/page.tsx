import { login, signup } from './actions'
import { Bot, MailCheck } from 'lucide-react'
import Link from 'next/link'

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ message: string; mode: string }>
}) {
  const params = await searchParams
  const message = params.message
  const mode = params.mode || 'login'

  const isSignup = mode === 'signup'

  if (message === 'check_email') {
    return (
      <div className="min-h-screen bg-black text-white flex flex-col justify-center items-center p-4 relative overflow-hidden">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-blue-900/20 blur-[120px] rounded-full pointer-events-none z-0" />
        
        <div className="glass-panel p-8 rounded-3xl w-full max-w-md relative z-10 flex flex-col items-center text-center">
          <div className="w-16 h-16 rounded-full bg-green-500/20 flex items-center justify-center mb-6">
            <MailCheck className="w-8 h-8 text-green-400" />
          </div>
          <h1 className="text-2xl font-bold mb-4">Письмо отправлено!</h1>
          <p className="text-gray-400 mb-8">
            Мы отправили ссылку для подтверждения на вашу почту. Пожалуйста, перейдите по ней, чтобы завершить регистрацию.
          </p>
          <Link 
            href="/login"
            className="w-full bg-white/5 hover:bg-white/10 text-white rounded-xl py-3 font-medium transition-colors block text-center"
          >
            Вернуться ко входу
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-black text-white flex flex-col justify-center items-center p-4 relative overflow-hidden">
      {/* Background ambient */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-blue-900/20 blur-[120px] rounded-full pointer-events-none z-0" />

      <div className="glass-panel p-8 rounded-3xl w-full max-w-md relative z-10">
        <div className="flex flex-col items-center mb-8">
          <div className="w-12 h-12 rounded-full bg-blue-500/20 flex items-center justify-center mb-4">
            <Bot className="w-6 h-6 text-blue-400" />
          </div>
          <h1 className="text-2xl font-bold">
            {isSignup ? 'Регистрация' : 'Вход в ИИ с руками'}
          </h1>
          <p className="text-gray-400 text-sm mt-2 text-center">
            {isSignup 
              ? 'Создайте аккаунт, чтобы получить свои 50 бесплатных кредитов' 
              : 'Войдите в свой аккаунт для продолжения работы'}
          </p>
        </div>

        {/* Tabs */}
        <div className="flex bg-white/5 p-1 rounded-xl mb-6">
          <Link 
            href="/login?mode=login" 
            className={`flex-1 text-center py-2 rounded-lg text-sm font-medium transition-colors ${!isSignup ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'}`}
          >
            Вход
          </Link>
          <Link 
            href="/login?mode=signup" 
            className={`flex-1 text-center py-2 rounded-lg text-sm font-medium transition-colors ${isSignup ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'}`}
          >
            Регистрация
          </Link>
        </div>

        <form className="flex flex-col gap-4">
          <div className="flex flex-col gap-1">
            <label className="text-sm text-gray-400 ml-1">Email</label>
            <input
              id="email"
              name="email"
              type="email"
              required
              className="bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-blue-500 transition-colors"
              placeholder="you@example.com"
            />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-sm text-gray-400 ml-1">Пароль</label>
            <input
              id="password"
              name="password"
              type="password"
              required
              className="bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-blue-500 transition-colors"
              placeholder="••••••••"
            />
          </div>

          {message && message !== 'check_email' && (
            <div className="bg-red-500/10 border border-red-500/50 text-red-400 text-sm p-3 rounded-lg text-center">
              {message}
            </div>
          )}

          <div className="flex flex-col gap-2 mt-4">
            <button
              formAction={isSignup ? signup : login}
              className="bg-blue-600 hover:bg-blue-700 text-white rounded-xl py-3 font-medium transition-colors"
            >
              {isSignup ? 'Зарегистрироваться' : 'Войти'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
