const { createApp } = Vue;

// Match the OS light/dark preference so the palette feels native.
const applyTheme = () => {
  const dark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  document.documentElement.setAttribute("data-theme", dark ? "dark" : "light");
};
applyTheme();
if (window.matchMedia) {
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", applyTheme);
}

createApp({
  data() {
    return {
      manifest: [],          // [{ id, name, file }]
      selectedDeckIds: [],
      shuffle: true,
      cards: [],             // merged, each tagged with deckName
      index: 0,
      flipped: false,        // is the card showing its back (answer)?
      chosen: null,          // MC selected option index
      screen: "picker",      // 'picker' | 'card' | 'done'
      loading: true,
      starting: false,
      error: "",
    };
  },

  computed: {
    current() {
      return this.cards[this.index] || {};
    },
    progressPercent() {
      if (!this.cards.length) return 0;
      return ((this.index + 1) / this.cards.length) * 100;
    },
    startLabel() {
      const n = this.selectedDeckIds.length;
      if (n === 0) return "請選擇牌組後開始";
      return n === 1 ? "開始" : `開始（${n} 個牌組）`;
    },
    // Text shown on the answer (back) face of an open-ended card.
    backAnswer() {
      return this.current.answer;
    },
  },

  methods: {
    async loadManifest() {
      this.loading = true;
      this.error = "";
      try {
        const res = await fetch("./decks/manifest.json");
        if (!res.ok) throw new Error(`Manifest request failed (${res.status}).`);
        const data = await res.json();
        this.manifest = Array.isArray(data.decks) ? data.decks : [];
        if (!this.manifest.length) {
          this.error = "清單中還沒有牌組。";
        }
      } catch (e) {
        this.error = `無法載入牌組列表。${e.message}`;
      } finally {
        this.loading = false;
      }
    },

    async start() {
      if (!this.selectedDeckIds.length) return;
      this.starting = true;
      this.error = "";
      try {
        const chosenDecks = this.manifest.filter((d) => this.selectedDeckIds.includes(d.id));
        const loaded = await Promise.all(
          chosenDecks.map(async (deck) => {
            const res = await fetch(deck.file);
            if (!res.ok) throw new Error(`"${deck.name}" failed to load (${res.status}).`);
            const data = await res.json();
            const cards = Array.isArray(data) ? data : (data.cards || []);
            return cards.map((card) => ({
              ...card,
              type: card.type || "open",
              deckName: data.name || deck.name,
            }));
          })
        );

        let merged = loaded.flat();
        if (!merged.length) throw new Error("所選牌組中沒有卡片。");
        if (this.shuffle) merged = this.shuffled(merged);

        this.cards = merged;
        this.index = 0;
        this.resetCardState();
        this.screen = "card";
      } catch (e) {
        this.error = `無法開始學習。${e.message}`;
        this.screen = "picker";
      } finally {
        this.starting = false;
      }
    },

    // Fisher–Yates, on a copy.
    shuffled(arr) {
      const a = arr.slice();
      for (let i = a.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [a[i], a[j]] = [a[j], a[i]];
      }
      return a;
    },

    resetCardState() {
      this.flipped = false;
      this.chosen = null;
    },

    selectOption(i) {
      if (this.chosen !== null) return; // lock in the first choice
      this.chosen = i;
    },

    flip() {
      this.flipped = !this.flipped;
    },

    // Clicking the card flips it (MC option buttons stop propagation).
    onCardClick() {
      this.flip();
    },

    optionClass(i) {
      if (this.chosen === null) return "";
      if (i === this.current.answer) return "correct";
      if (i === this.chosen) return "wrong";
      return "dim";
    },

    optionMark(i) {
      if (this.chosen !== null) {
        if (i === this.current.answer) return "✓";
        if (i === this.chosen) return "✗";
      }
      return String.fromCharCode(65 + i); // A, B, C, D…
    },

    next() {
      if (this.index + 1 >= this.cards.length) {
        this.screen = "done";
        return;
      }
      this.index++;
      this.resetCardState();
    },

    prev() {
      if (this.index === 0) return;
      this.index--;
      this.resetCardState();
    },

    restartSame() {
      if (this.shuffle) this.cards = this.shuffled(this.cards);
      this.index = 0;
      this.resetCardState();
      this.screen = "card";
    },

    restart() {
      this.screen = "picker";
      this.cards = [];
      this.index = 0;
      this.resetCardState();
    },
  },

  mounted() {
    this.loadManifest();
  },
}).mount("#app");
