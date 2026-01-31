import { TextCorrector } from "@/components/TextCorrector";

export default function Home() {
  return (
    <main className="mx-auto max-w-3xl px-4 py-12">
      <h1 className="mb-2 text-3xl font-bold tracking-tight">
        Text Corrector
      </h1>
      <p className="mb-8 text-gray-500">
        Fix grammar and convert between British and American English.
      </p>
      <TextCorrector />
    </main>
  );
}
