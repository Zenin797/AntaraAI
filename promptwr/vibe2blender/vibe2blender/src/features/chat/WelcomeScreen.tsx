export const WelcomeScreen = ({ onSelectExample }: { onSelectExample: (prompt: string) => void }) => {
  const examples = [
    {
      title: "Low-Poly Neon Sword",
      prompt: "Generate a low-poly neon sword with a glowing emissive material and a subsurf modifier for slight rounded edges.",
      icon: "⚔️"
    },
    {
      title: "Sci-Fi Cyberpunk Crate",
      prompt: "Create a sci-fi cyberpunk crate with complex paneling details using bpy.ops.mesh.primitive_cube_add and bevel modifiers.",
      icon: "📦"
    },
    {
      title: "Smooth Ceramic Vase",
      prompt: "Make a smooth ceramic vase using a spin operator or a lathe-like approach with a high-resolution subsurf modifier.",
      icon: "🏺"
    }
  ];

  return (
    <div className="flex flex-col items-center justify-center h-full py-12 px-6 text-center animate-fade-in">
      <div className="mb-8 p-4 border-2 border-text bg-text text-bg font-black text-4xl tracking-tighter">
        VIBE2BLENDER
      </div>
      
      <h3 className="text-xl font-bold mb-2 tracking-tighter">READY TO BUILD IN 3D?</h3>
      <p className="text-accent text-sm mb-12 max-w-sm">
        Select a stock example below to see the workflow or type your own concept in the chat.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full max-w-3xl">
        {examples.map((example, idx) => (
          <button
            key={idx}
            onClick={() => onSelectExample(example.prompt)}
            className="group flex flex-col p-6 border border-border bg-secondary/30 hover:bg-text hover:text-bg transition-all text-left"
          >
            <span className="text-2xl mb-4 grayscale group-hover:grayscale-0 transition-all">{example.icon}</span>
            <span className="text-xs font-bold uppercase tracking-widest mb-2 text-accent group-hover:text-bg/50">STOCK EXAMPLE</span>
            <span className="text-sm font-bold group-hover:text-bg">{example.title}</span>
          </button>
        ))}
      </div>
    </div>
  );
};
