...
class FastWhisperTranscriber:
    """Performance-optimized Whisper transcriber."""
    
    # Class-level model cache to reuse models across instances
    _model_cache = {}
    
    def __init__(self, model_size: str = "base", device: Optional[str] = None):
        """
        Initialize the Fast Whisper transcriber.

        Args:
            model_size: Whisper model size to use or path to a local .bin file
            device: Device to use ('cuda', 'cpu', 'mps', or None for auto-detection)
        """
        self.model_size = model_size
        self.device = self._get_optimal_device(device)
        self.model = None

        print("Initializing Fast Whisper transcriber...")
        print(f"Model: {self.model_size}")
        print(f"Device: {self.device}")

        self._load_or_get_cached_model()
    
    def _load_or_get_cached_model(self):
        """Load model or get from cache for performance."""
        # Use the file path as cache key if it's a local bin file
        if os.path.isfile(self.model_size) and self.model_size.endswith('.bin'):
            cache_key = f"{self.model_size}_{self.device}"
        else:
            cache_key = f"{self.model_size}_{self.device}"
        
        if cache_key in self._model_cache:
            print(f"Using cached model ({self.model_size}) (instant load)")
            self.model = self._model_cache[cache_key]
            return
        
        print(f"Loading model: {self.model_size} ...")
        start_time = time.time()
        
        try:
            # If model_size is a path to .bin, load from file
            if os.path.isfile(self.model_size) and self.model_size.endswith('.bin'):
                print(f"Loading model from local file: {self.model_size}")
                self.model = whisper.load_model(self.model_size, device=self.device)
            else:
                self.model = whisper.load_model(self.model_size, device=self.device)
            
            # Cache the model for reuse
            self._model_cache[cache_key] = self.model
            
            load_time = time.time() - start_time
            print(f"Model loaded and cached in {load_time:.2f} seconds")
            
        except Exception as e:
            error_str = str(e).lower()
            # If MPS fails, fall back to CPU
            if self.device == "mps" and ("mps" in error_str or "sparse" in error_str):
                print(f"MPS device failed ({e}), falling back to CPU...")
                self.device = "cpu"
                cache_key = f"{self.model_size}_{self.device}"
                try:
                    self.model = whisper.load_model(self.model_size, device=self.device)
                    self._model_cache[cache_key] = self.model
                    load_time = time.time() - start_time
                    print(f"Model loaded on CPU in {load_time:.2f} seconds")
                except Exception as cpu_error:
                    print(f"Error loading model on CPU: {cpu_error}")
                    sys.exit(1)
            else:
                print(f"Error loading model: {e}")
                sys.exit(1)
...
