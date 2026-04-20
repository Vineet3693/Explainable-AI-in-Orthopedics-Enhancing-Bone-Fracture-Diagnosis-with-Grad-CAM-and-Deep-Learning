import { createTheme } from '@mui/material/styles';

/**
 * VIBRANT & ENGAGING Medical AI Theme
 * 
 * WHY VIBRANT COLORS:
 * - Eye-catching gradients for modern feel
 * - Bright, energetic palette for engagement
 * - Professional yet exciting
 * - Memorable user experience
 */

export const theme = createTheme({
    palette: {
        primary: {
            main: '#00D4FF',      // Bright cyan - vibrant and modern
            light: '#5DFDFF',
            dark: '#00A3CC',
            contrastText: '#FFFFFF',
        },
        secondary: {
            main: '#FF6B9D',      // Hot pink - energetic and bold
            light: '#FFB3D1',
            dark: '#CC3366',
            contrastText: '#FFFFFF',
        },
        success: {
            main: '#00E676',      // Bright green - vibrant success
            light: '#69F0AE',
            dark: '#00C853',
        },
        error: {
            main: '#FF3D71',      // Bright red - attention-grabbing
            light: '#FF708D',
            dark: '#CC1744',
        },
        warning: {
            main: '#FFB800',      // Golden yellow - warm and inviting
            light: '#FFD54F',
            dark: '#FF8F00',
        },
        info: {
            main: '#7C4DFF',      // Purple - creative and modern
            light: '#B47CFF',
            dark: '#5E35B1',
        },
        background: {
            default: '#F8F9FF',   // Subtle blue tint
            paper: '#FFFFFF',
        },
        text: {
            primary: '#1A1A2E',   // Deep navy
            secondary: '#4A5568',
        },
    },
    typography: {
        fontFamily: '"Poppins", "Inter", "Roboto", sans-serif',
        h1: {
            fontSize: '3rem',
            fontWeight: 800,
            lineHeight: 1.2,
            background: 'linear-gradient(135deg, #00D4FF 0%, #FF6B9D 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
        },
        h2: {
            fontSize: '2.5rem',
            fontWeight: 700,
            lineHeight: 1.3,
        },
        h3: {
            fontSize: '2rem',
            fontWeight: 600,
            lineHeight: 1.4,
        },
        h4: {
            fontSize: '1.5rem',
            fontWeight: 600,
            lineHeight: 1.4,
        },
        h5: {
            fontSize: '1.25rem',
            fontWeight: 500,
            lineHeight: 1.5,
        },
        body1: {
            fontSize: '1rem',
            lineHeight: 1.6,
        },
    },
    shape: {
        borderRadius: 16,
    },
    components: {
        MuiButton: {
            styleOverrides: {
                root: {
                    textTransform: 'none',
                    fontWeight: 600,
                    borderRadius: 12,
                    padding: '12px 32px',
                    fontSize: '1rem',
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    '&:hover': {
                        transform: 'translateY(-2px)',
                        boxShadow: '0 8px 24px rgba(0, 212, 255, 0.3)',
                    },
                },
                contained: {
                    background: 'linear-gradient(135deg, #00D4FF 0%, #7C4DFF 100%)',
                    boxShadow: '0 4px 16px rgba(0, 212, 255, 0.3)',
                    '&:hover': {
                        background: 'linear-gradient(135deg, #00A3CC 0%, #5E35B1 100%)',
                        boxShadow: '0 8px 32px rgba(0, 212, 255, 0.4)',
                    },
                },
                outlined: {
                    borderWidth: 2,
                    borderColor: '#00D4FF',
                    '&:hover': {
                        borderWidth: 2,
                        background: 'rgba(0, 212, 255, 0.08)',
                    },
                },
            },
        },
        MuiCard: {
            styleOverrides: {
                root: {
                    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.08)',
                    borderRadius: 20,
                    border: '1px solid rgba(0, 212, 255, 0.1)',
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: '0 16px 48px rgba(0, 212, 255, 0.15)',
                    },
                },
            },
        },
        MuiPaper: {
            styleOverrides: {
                root: {
                    backgroundImage: 'none',
                },
                elevation1: {
                    boxShadow: '0 4px 16px rgba(0, 0, 0, 0.06)',
                },
                elevation2: {
                    boxShadow: '0 8px 24px rgba(0, 0, 0, 0.08)',
                },
            },
        },
        MuiChip: {
            styleOverrides: {
                root: {
                    fontWeight: 600,
                    borderRadius: 8,
                },
                colorPrimary: {
                    background: 'linear-gradient(135deg, #00D4FF 0%, #7C4DFF 100%)',
                    color: '#FFFFFF',
                },
                colorSecondary: {
                    background: 'linear-gradient(135deg, #FF6B9D 0%, #FFB800 100%)',
                    color: '#FFFFFF',
                },
            },
        },
        MuiLinearProgress: {
            styleOverrides: {
                root: {
                    height: 8,
                    borderRadius: 4,
                    backgroundColor: 'rgba(0, 212, 255, 0.1)',
                },
                bar: {
                    borderRadius: 4,
                    background: 'linear-gradient(90deg, #00D4FF 0%, #7C4DFF 100%)',
                },
            },
        },
    },
});

// Custom gradient backgrounds for different sections
export const gradients = {
    primary: 'linear-gradient(135deg, #00D4FF 0%, #7C4DFF 100%)',
    secondary: 'linear-gradient(135deg, #FF6B9D 0%, #FFB800 100%)',
    success: 'linear-gradient(135deg, #00E676 0%, #00D4FF 100%)',
    error: 'linear-gradient(135deg, #FF3D71 0%, #FF6B9D 100%)',
    hero: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    card: 'linear-gradient(135deg, rgba(0, 212, 255, 0.05) 0%, rgba(124, 77, 255, 0.05) 100%)',
};

// Animation keyframes
export const animations = {
    float: `
    @keyframes float {
      0%, 100% { transform: translateY(0px); }
      50% { transform: translateY(-20px); }
    }
  `,
    pulse: `
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.5; }
    }
  `,
    shimmer: `
    @keyframes shimmer {
      0% { background-position: -1000px 0; }
      100% { background-position: 1000px 0; }
    }
  `,
    slideIn: `
    @keyframes slideIn {
      from {
        opacity: 0;
        transform: translateX(-30px);
      }
      to {
        opacity: 1;
        transform: translateX(0);
      }
    }
  `,
};
