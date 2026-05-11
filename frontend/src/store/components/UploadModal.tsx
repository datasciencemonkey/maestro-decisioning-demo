import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { X, Loader2 } from 'lucide-react'

const presetPhotos = [
  'https://images.unsplash.com/photo-1574158622682-e40e69881006?w=400&h=400&fit=crop',
  'https://images.unsplash.com/photo-1573865526739-10659fec78a5?w=400&h=400&fit=crop',
  'https://images.unsplash.com/photo-1495360010541-f48722b34f7d?w=400&h=400&fit=crop',
  'https://images.unsplash.com/photo-1526336024174-e58f5cdd8e13?w=400&h=400&fit=crop',
]

interface UploadModalProps {
  isOpen: boolean
  onClose: () => void
  onMatch: () => void
}

export default function UploadModal({ isOpen, onClose, onMatch }: UploadModalProps) {
  const [analyzing, setAnalyzing] = useState(false)

  const handleSelect = () => {
    setAnalyzing(true)
    setTimeout(() => {
      setAnalyzing(false)
      onMatch()
      onClose()
    }, 1200)
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={onClose}
            className="fixed inset-0 bg-[#0D0B09]/50 backdrop-blur-sm z-50 cursor-pointer"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.92, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.92, y: 20 }}
            transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-50 bg-card rounded-2xl p-8 shadow-2xl max-w-md w-full"
          >
            {/* Header */}
            <div className="flex items-center justify-between mb-5">
              <h3 className="font-serif text-lg">Match My Pet</h3>
              <button
                onClick={onClose}
                className="p-1.5 rounded-lg hover:bg-secondary transition-colors cursor-pointer"
                aria-label="Close"
              >
                <X size={18} />
              </button>
            </div>

            {analyzing ? (
              /* Spinner state */
              <div className="flex flex-col items-center justify-center py-12 gap-4">
                <Loader2 size={32} className="text-gold animate-spin" />
                <p className="text-sm font-medium text-gold">Analyzing your pet...</p>
              </div>
            ) : (
              /* Photo grid */
              <>
                <p className="text-xs text-muted-foreground mb-4">
                  Select a photo of your pet to find matching products
                </p>
                <div className="grid grid-cols-2 gap-3">
                  {presetPhotos.map((url, i) => (
                    <button
                      key={i}
                      onClick={handleSelect}
                      className="aspect-square rounded-xl overflow-hidden cursor-pointer ring-2 ring-transparent hover:ring-[#C4A87A] transition-all duration-200 hover:scale-[1.02] active:scale-[0.98]"
                    >
                      <img
                        src={url}
                        alt={`Cat photo ${i + 1}`}
                        className="w-full h-full object-cover"
                      />
                    </button>
                  ))}
                </div>
              </>
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
