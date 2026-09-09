"use client";

import { useState } from "react";
import Image from "next/image";

export default function ArticleImage({ src, alt, priority }) {
  const [error, setError] = useState(false);

  if (error || !src) {
    return (
      <div className="flex h-44 w-full items-center justify-center bg-gradient-to-br from-blue-950 to-slate-900 text-5xl">
        🤖
      </div>
    );
  }

  return (
    <div className="relative h-44 w-full bg-slate-950">
      <Image
        src={src}
        alt={alt}
        fill
        unoptimized
        sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 430px"
        className="object-cover"
        priority={priority}
        onError={() => setError(true)}
      />
    </div>
  );
}
