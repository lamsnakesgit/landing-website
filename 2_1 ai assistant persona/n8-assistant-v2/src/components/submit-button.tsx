'use client'

import { useFormStatus } from 'react-dom'
import { Loader2 } from 'lucide-react'

interface SubmitButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode
}

export function SubmitButton({ children, formAction, ...props }: SubmitButtonProps) {
  const { pending } = useFormStatus()

  return (
    <button
      {...props}
      formAction={formAction}
      disabled={pending || props.disabled}
      className={`bg-blue-600 hover:bg-blue-700 text-white rounded-xl py-3 font-medium transition-colors flex items-center justify-center gap-2 ${props.className || ''}`}
    >
      {pending && <Loader2 className="w-5 h-5 animate-spin" />}
      {pending ? 'Загрузка...' : children}
    </button>
  )
}
