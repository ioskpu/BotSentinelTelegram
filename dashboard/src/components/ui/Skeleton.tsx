import React from 'react'

interface SkeletonProps {
  className?: string
}

export function Skeleton({ className = '' }: SkeletonProps) {
  return (
    <div
      className={`animate-pulse bg-crypto-bg-tertiary rounded-md ${className}`}
    />
  )
}

export default Skeleton
