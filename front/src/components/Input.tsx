import './Input.css'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
}

export function Input({ label, error, id, className = '', ...props }: InputProps) {
  const inputId = id ?? label?.toLowerCase().replace(/\s+/g, '-')

  return (
    <label className={`field ${className}`.trim()} htmlFor={inputId}>
      {label ? <span className="field__label">{label}</span> : null}
      <input id={inputId} className={`field__input ${error ? 'field__input--error' : ''}`} {...props} />
      {error ? <span className="field__error">{error}</span> : null}
    </label>
  )
}

interface FileInputProps extends Omit<InputProps, 'type'> {
  accept?: string
  onFileChange: (file: File | null) => void
}

export function FileInput({ label, error, accept, onFileChange, className = '' }: FileInputProps) {
  return (
    <label className={`field field--file ${className}`.trim()}>
      {label ? <span className="field__label">{label}</span> : null}
      <input
        type="file"
        className="field__file"
        accept={accept}
        onChange={(e) => onFileChange(e.target.files?.[0] ?? null)}
      />
      {error ? <span className="field__error">{error}</span> : null}
    </label>
  )
}
