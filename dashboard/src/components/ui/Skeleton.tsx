interface SkeletonProps {
  className?: string
}

export function Skeleton({ className = '' }: SkeletonProps) {
  return (
    <div
      role="status"
      className={`animate-pulse bg-crypto-bg-tertiary rounded-md ${className}`}
    />
  )
}

export default Skeleton
