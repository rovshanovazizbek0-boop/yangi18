"use client";

import { useState } from "react";
import Image from "next/image";

export default function SingleArticleImage({ src, alt }) {
  const [error, setError] = useState(false);

  if (error || !src) return null;

  return (
    <div className="relative mb-6 aspect-video overflow-hidden rounded-xl bg-slate-900">
      <Image
        src={src}
        alt={alt}
        fill
        unoptimized
        sizes="(max-width: 768px) 100vw, 768px"
        className="object-cover"
        priority
        onError={() => setError(true)}
      />
    </div>
  );
}
