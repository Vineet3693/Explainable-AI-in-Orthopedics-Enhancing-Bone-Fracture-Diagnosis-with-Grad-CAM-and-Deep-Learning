import React from 'react';
import {
    Box,
    Container,
    Typography,
    Button,
    Grid,
    Card,
    CardContent,
    CardActions,
    alpha,
    useTheme,
} from '@mui/material';
import {
    CloudUpload,
    Speed,
    Security,
    Psychology,
    TrendingUp,
    Verified,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const features = [
    {
        icon: <Speed sx={{ fontSize: 48 }} />,
        title: 'Lightning Fast',
        description: 'Get results in under 2 seconds with our optimized AI models',
        gradient: 'linear-gradient(135deg, #00D4FF 0%, #7C4DFF 100%)',
    },
    {
        icon: <Psychology sx={{ fontSize: 48 }} />,
        title: 'AI-Powered',
        description: 'Advanced deep learning models trained on 100,000+ X-rays',
        gradient: 'linear-gradient(135deg, #FF6B9D 0%, #FFB800 100%)',
    },
    {
        icon: <Security sx={{ fontSize: 48 }} />,
        title: 'HIPAA Compliant',
        description: 'Enterprise-grade security and privacy protection',
        gradient: 'linear-gradient(135deg, #00E676 0%, #00D4FF 100%)',
    },
    {
        icon: <Verified sx={{ fontSize: 48 }} />,
        title: '94.5% Accuracy',
        description: 'Clinically validated with radiologist-level performance',
        gradient: 'linear-gradient(135deg, #7C4DFF 0%, #FF6B9D 100%)',
    },
];

const HomePage: React.FC = () => {
    const navigate = useNavigate();
    const theme = useTheme();

    return (
        <Box>
            {/* Hero Section with animated gradient */}
            <Box
                sx={{
                    position: 'relative',
                    overflow: 'hidden',
                    borderRadius: 4,
                    mb: 6,
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    color: '#FFFFFF',
                    py: 8,
                    px: 4,
                    '&::before': {
                        content: '""',
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        background: 'radial-gradient(circle at 20% 50%, rgba(255, 107, 157, 0.3) 0%, transparent 50%)',
                        animation: 'pulse 4s ease-in-out infinite',
                    },
                }}
            >
                <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1 }}>
                    <Grid container spacing={4} alignItems="center">
                        <Grid item xs={12} md={7}>
                            <Typography
                                variant="h1"
                                sx={{
                                    mb: 3,
                                    fontWeight: 800,
                                    fontSize: { xs: '2.5rem', md: '3.5rem' },
                                    background: 'linear-gradient(135deg, #FFFFFF 0%, #FFB3D1 100%)',
                                    WebkitBackgroundClip: 'text',
                                    WebkitTextFillColor: 'transparent',
                                    animation: 'slideIn 0.8s ease-out',
                                }}
                            >
                                AI-Powered Fracture Detection
                            </Typography>

                            <Typography
                                variant="h5"
                                sx={{
                                    mb: 4,
                                    opacity: 0.95,
                                    fontWeight: 400,
                                    animation: 'slideIn 1s ease-out',
                                }}
                            >
                                Revolutionary medical imaging analysis powered by cutting-edge artificial intelligence
                            </Typography>

                            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                                <Button
                                    variant="contained"
                                    size="large"
                                    startIcon={<CloudUpload />}
                                    onClick={() => navigate('/upload')}
                                    sx={{
                                        background: 'linear-gradient(135deg, #00D4FF 0%, #7C4DFF 100%)',
                                        px: 4,
                                        py: 1.5,
                                        fontSize: '1.1rem',
                                        fontWeight: 600,
                                        boxShadow: '0 8px 32px rgba(0, 212, 255, 0.4)',
                                        '&:hover': {
                                            background: 'linear-gradient(135deg, #00A3CC 0%, #5E35B1 100%)',
                                            transform: 'translateY(-4px)',
                                            boxShadow: '0 12px 40px rgba(0, 212, 255, 0.5)',
                                        },
                                    }}
                                >
                                    Upload X-Ray Now
                                </Button>

                                <Button
                                    variant="outlined"
                                    size="large"
                                    onClick={() => navigate('/history')}
                                    sx={{
                                        borderColor: '#FFFFFF',
                                        color: '#FFFFFF',
                                        borderWidth: 2,
                                        px: 4,
                                        py: 1.5,
                                        fontSize: '1.1rem',
                                        '&:hover': {
                                            borderWidth: 2,
                                            borderColor: '#FFFFFF',
                                            background: 'rgba(255, 255, 255, 0.1)',
                                        },
                                    }}
                                >
                                    View History
                                </Button>
                            </Box>
                        </Grid>

                        <Grid item xs={12} md={5}>
                            <Box
                                sx={{
                                    position: 'relative',
                                    animation: 'float 6s ease-in-out infinite',
                                }}
                            >
                                {/* Decorative circles */}
                                <Box
                                    sx={{
                                        position: 'absolute',
                                        top: '10%',
                                        right: '10%',
                                        width: 200,
                                        height: 200,
                                        borderRadius: '50%',
                                        background: 'linear-gradient(135deg, #00D4FF 0%, #7C4DFF 100%)',
                                        opacity: 0.2,
                                        filter: 'blur(40px)',
                                    }}
                                />
                                <Box
                                    sx={{
                                        position: 'absolute',
                                        bottom: '10%',
                                        left: '10%',
                                        width: 150,
                                        height: 150,
                                        borderRadius: '50%',
                                        background: 'linear-gradient(135deg, #FF6B9D 0%, #FFB800 100%)',
                                        opacity: 0.2,
                                        filter: 'blur(40px)',
                                    }}
                                />
                            </Box>
                        </Grid>
                    </Grid>
                </Container>
            </Box>

            {/* Features Grid */}
            <Container maxWidth="lg">
                <Typography
                    variant="h3"
                    align="center"
                    sx={{
                        mb: 6,
                        fontWeight: 700,
                        background: 'linear-gradient(135deg, #00D4FF 0%, #FF6B9D 100%)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                    }}
                >
                    Why Choose Our Platform?
                </Typography>

                <Grid container spacing={4}>
                    {features.map((feature, index) => (
                        <Grid item xs={12} sm={6} md={3} key={index}>
                            <Card
                                className="hover-lift"
                                sx={{
                                    height: '100%',
                                    borderRadius: 4,
                                    border: '1px solid',
                                    borderColor: alpha(theme.palette.primary.main, 0.1),
                                    background: 'rgba(255, 255, 255, 0.9)',
                                    backdropFilter: 'blur(10px)',
                                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                                    animation: `slideIn ${0.5 + index * 0.1}s ease-out`,
                                    '&:hover': {
                                        borderColor: theme.palette.primary.main,
                                        '& .feature-icon': {
                                            transform: 'scale(1.1) rotate(5deg)',
                                        },
                                    },
                                }}
                            >
                                <CardContent sx={{ textAlign: 'center', p: 4 }}>
                                    <Box
                                        className="feature-icon"
                                        sx={{
                                            display: 'inline-flex',
                                            p: 2,
                                            borderRadius: 3,
                                            background: feature.gradient,
                                            color: '#FFFFFF',
                                            mb: 2,
                                            transition: 'transform 0.3s ease',
                                        }}
                                    >
                                        {feature.icon}
                                    </Box>

                                    <Typography
                                        variant="h6"
                                        sx={{ mb: 1, fontWeight: 600 }}
                                    >
                                        {feature.title}
                                    </Typography>

                                    <Typography
                                        variant="body2"
                                        color="text.secondary"
                                    >
                                        {feature.description}
                                    </Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                    ))}
                </Grid>

                {/* Stats Section */}
                <Box
                    sx={{
                        mt: 8,
                        p: 6,
                        borderRadius: 4,
                        background: 'linear-gradient(135deg, rgba(0, 212, 255, 0.05) 0%, rgba(124, 77, 255, 0.05) 100%)',
                        border: '1px solid',
                        borderColor: alpha(theme.palette.primary.main, 0.1),
                    }}
                >
                    <Grid container spacing={4} textAlign="center">
                        <Grid item xs={12} md={4}>
                            <Typography
                                variant="h2"
                                sx={{
                                    fontWeight: 800,
                                    background: 'linear-gradient(135deg, #00D4FF 0%, #7C4DFF 100%)',
                                    WebkitBackgroundClip: 'text',
                                    WebkitTextFillColor: 'transparent',
                                }}
                            >
                                100K+
                            </Typography>
                            <Typography variant="h6" color="text.secondary">
                                X-Rays Analyzed
                            </Typography>
                        </Grid>

                        <Grid item xs={12} md={4}>
                            <Typography
                                variant="h2"
                                sx={{
                                    fontWeight: 800,
                                    background: 'linear-gradient(135deg, #FF6B9D 0%, #FFB800 100%)',
                                    WebkitBackgroundClip: 'text',
                                    WebkitTextFillColor: 'transparent',
                                }}
                            >
                                94.5%
                            </Typography>
                            <Typography variant="h6" color="text.secondary">
                                Accuracy Rate
                            </Typography>
                        </Grid>

                        <Grid item xs={12} md={4}>
                            <Typography
                                variant="h2"
                                sx={{
                                    fontWeight: 800,
                                    background: 'linear-gradient(135deg, #00E676 0%, #00D4FF 100%)',
                                    WebkitBackgroundClip: 'text',
                                    WebkitTextFillColor: 'transparent',
                                }}
                            >
                                &lt;2s
                            </Typography>
                            <Typography variant="h6" color="text.secondary">
                                Analysis Time
                            </Typography>
                        </Grid>
                    </Grid>
                </Box>
            </Container>
        </Box>
    );
};

export default HomePage;
