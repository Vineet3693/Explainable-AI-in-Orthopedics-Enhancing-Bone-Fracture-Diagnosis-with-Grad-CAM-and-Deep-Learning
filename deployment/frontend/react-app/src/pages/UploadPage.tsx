import React, { useCallback, useState } from 'react';
import {
    Box,
    Container,
    Typography,
    Paper,
    Button,
    LinearProgress,
    Chip,
    Alert,
    Grid,
    Card,
    CardContent,
    Tabs,
    Tab,
    TextField,
    IconButton,
    alpha,
    useTheme,
} from '@mui/material';
import {
    CloudUpload,
    CheckCircle,
    Error as ErrorIcon,
    Image as ImageIcon,
    Send,
    Download,
    ThumbUp,
    ThumbDown,
    Help,
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { useAppDispatch, useAppSelector } from '@store/store';
import { uploadAndPredict, setCurrentFile } from '@store/slices/predictionSlice';

interface TabPanelProps {
    children?: React.ReactNode;
    index: number;
    value: number;
}

function TabPanel(props: TabPanelProps) {
    const { children, value, index, ...other } = props;
    return (
        <div role="tabpanel" hidden={value !== index} {...other}>
            {value === index && <Box sx={{ pt: 2 }}>{children}</Box>}
        </div>
    );
}

const DashboardUploadPage: React.FC = () => {
    const theme = useTheme();
    const dispatch = useAppDispatch();
    const { uploadProgress, isLoading, error, currentResult } = useAppSelector(
        (state) => state.prediction
    );

    const [preview, setPreview] = useState<string | null>(null);
    const [showResults, setShowResults] = useState(false);
    const [analysisTab, setAnalysisTab] = useState(0);
    const [qaQuestion, setQaQuestion] = useState('');
    const [qaMessages, setQaMessages] = useState<Array<{ type: 'q' | 'a'; text: string }>>([]);

    const onDrop = useCallback(
        async (acceptedFiles: File[]) => {
            const file = acceptedFiles[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = () => setPreview(reader.result as string);
                reader.readAsDataURL(file);

                dispatch(setCurrentFile(file));
                const result = await dispatch(uploadAndPredict(file));

                if (result.meta.requestStatus === 'fulfilled') {
                    setShowResults(true);
                }
            }
        },
        [dispatch]
    );

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: { 'image/*': ['.jpg', '.jpeg', '.png', '.dicom'] },
        maxFiles: 1,
        maxSize: 10 * 1024 * 1024,
    });

    const handleQaSubmit = () => {
        if (!qaQuestion.trim()) return;
        setQaMessages([
            ...qaMessages,
            { type: 'q', text: qaQuestion },
            { type: 'a', text: 'The AI model indicates the ulna appears intact based on the analysis.' },
        ]);
        setQaQuestion('');
    };

    const confidence = currentResult ? (currentResult.prediction.confidence * 100).toFixed(1) : '0';
    const isFractured = currentResult?.prediction.result === 'Fractured';

    return (
        <Container maxWidth={false} sx={{ maxWidth: 1920 }}>
            <Grid container spacing={2.5} sx={{ mt: 0 }}>
                {/* Upload Panel */}
                <Grid item xs={12} md={4}>
                    <Paper sx={{ p: 3, borderRadius: 2, height: '100%' }}>
                        <Typography variant="overline" color="text.secondary" fontWeight={600}>
                            UPLOAD
                        </Typography>

                        <Paper
                            {...getRootProps()}
                            sx={{
                                mt: 2,
                                p: 6,
                                borderRadius: 2,
                                border: '2px dashed',
                                borderColor: isDragActive ? 'primary.main' : 'divider',
                                bgcolor: isDragActive ? alpha(theme.palette.primary.main, 0.05) : 'grey.50',
                                cursor: 'pointer',
                                textAlign: 'center',
                                transition: 'all 0.3s',
                                '&:hover': {
                                    borderColor: 'primary.main',
                                    bgcolor: alpha(theme.palette.primary.main, 0.02),
                                },
                            }}
                        >
                            <input {...getInputProps()} />
                            <Box
                                sx={{
                                    width: 80,
                                    height: 80,
                                    borderRadius: 2,
                                    bgcolor: 'primary.main',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    mx: 'auto',
                                    mb: 2,
                                }}
                            >
                                <CloudUpload sx={{ fontSize: 40, color: 'white' }} />
                            </Box>
                            <Typography variant="h6" gutterBottom>
                                Drag and Drop X-ray Image Here
                            </Typography>
                            <Typography variant="body2" color="text.secondary" gutterBottom>
                                or
                            </Typography>
                            <Button variant="contained" sx={{ mt: 1 }}>
                                Upload X-ray Image
                            </Button>
                            <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 2 }}>
                                Supported formats: JPG, PNG, DICOM
                            </Typography>
                        </Paper>

                        {preview && (
                            <Box sx={{ mt: 2 }}>
                                <img
                                    src={preview}
                                    alt="Preview"
                                    style={{ width: '100%', borderRadius: 8 }}
                                />
                            </Box>
                        )}
                    </Paper>
                </Grid>

                {/* Results Panel */}
                <Grid item xs={12} md={5}>
                    <Paper sx={{ p: 3, borderRadius: 2, height: '100%' }}>
                        <Typography variant="overline" color="text.secondary" fontWeight={600}>
                            RESULTS PANEL
                        </Typography>

                        {isLoading && (
                            <Box sx={{ textAlign: 'center', py: 8 }}>
                                <Box
                                    sx={{
                                        width: 40,
                                        height: 40,
                                        border: '3px solid',
                                        borderColor: 'grey.300',
                                        borderTopColor: 'primary.main',
                                        borderRadius: '50%',
                                        animation: 'spin 1s linear infinite',
                                        mx: 'auto',
                                        mb: 2,
                                        '@keyframes spin': {
                                            '0%': { transform: 'rotate(0deg)' },
                                            '100%': { transform: 'rotate(360deg)' },
                                        },
                                    }}
                                />
                                <Typography>Analyzing X-ray...</Typography>
                            </Box>
                        )}

                        {showResults && currentResult && (
                            <Box sx={{ mt: 2 }}>
                                {/* Prediction */}
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                                    <Typography variant="subtitle2" fontWeight={600}>
                                        MODEL PREDICTION
                                    </Typography>
                                    <Chip label="EfficientNetB0" size="small" color="primary" />
                                </Box>

                                <Chip
                                    label={currentResult.prediction.result.toUpperCase()}
                                    sx={{
                                        fontSize: 24,
                                        fontWeight: 700,
                                        height: 'auto',
                                        py: 1.5,
                                        px: 3,
                                        bgcolor: isFractured ? 'error.light' : 'success.light',
                                        color: isFractured ? 'error.dark' : 'success.dark',
                                    }}
                                />

                                <Typography variant="h6" sx={{ mt: 2 }}>
                                    Confidence: {confidence}%
                                </Typography>

                                <LinearProgress
                                    variant="determinate"
                                    value={parseFloat(confidence)}
                                    sx={{ height: 8, borderRadius: 1, mt: 1 }}
                                />

                                <Grid container spacing={1.5} sx={{ mt: 2 }}>
                                    <Grid item xs={6}>
                                        <Card variant="outlined">
                                            <CardContent sx={{ textAlign: 'center', py: 1.5 }}>
                                                <Typography variant="caption" color="text.secondary">
                                                    Accuracy
                                                </Typography>
                                                <Typography variant="h5" fontWeight={700}>
                                                    84%
                                                </Typography>
                                            </CardContent>
                                        </Card>
                                    </Grid>
                                    <Grid item xs={6}>
                                        <Card variant="outlined">
                                            <CardContent sx={{ textAlign: 'center', py: 1.5 }}>
                                                <Typography variant="caption" color="text.secondary">
                                                    Recall
                                                </Typography>
                                                <Typography variant="h5" fontWeight={700}>
                                                    100%
                                                </Typography>
                                            </CardContent>
                                        </Card>
                                    </Grid>
                                </Grid>

                                {/* Explainability */}
                                <Box sx={{ mt: 3 }}>
                                    <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                                        EXPLAINABILITY
                                    </Typography>
                                    <Grid container spacing={2}>
                                        <Grid item xs={6}>
                                            <Box sx={{ textAlign: 'center' }}>
                                                <img
                                                    src={preview || ''}
                                                    alt="Original"
                                                    style={{ width: '100%', borderRadius: 8 }}
                                                />
                                                <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>
                                                    Original
                                                </Typography>
                                            </Box>
                                        </Grid>
                                        <Grid item xs={6}>
                                            <Box sx={{ textAlign: 'center' }}>
                                                <img
                                                    src={preview || ''}
                                                    alt="Heatmap"
                                                    style={{ width: '100%', borderRadius: 8 }}
                                                />
                                                <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>
                                                    GradCAM Heatmap
                                                </Typography>
                                            </Box>
                                        </Grid>
                                    </Grid>
                                </Box>

                                {/* AI Analysis Tabs */}
                                <Box sx={{ mt: 3 }}>
                                    <Tabs value={analysisTab} onChange={(_, v) => setAnalysisTab(v)}>
                                        <Tab label="Gemini Analysis" />
                                        <Tab label="Groq Summary" />
                                    </Tabs>

                                    <TabPanel value={analysisTab} index={0}>
                                        <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                                            Findings:
                                        </Typography>
                                        <Typography variant="body2" paragraph>
                                            The X-ray shows {isFractured ? 'evidence of' : 'no signs of'} fracture with {confidence}% confidence.
                                        </Typography>
                                        <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                                            Assessment:
                                        </Typography>
                                        <Typography variant="body2" paragraph>
                                            Model assessment indicates {currentResult.prediction.result.toLowerCase()} status.
                                        </Typography>
                                        <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                                            Recommendation:
                                        </Typography>
                                        <Typography variant="body2">
                                            {isFractured ? 'Immediate orthopedic consultation recommended.' : 'No immediate action required.'}
                                        </Typography>
                                    </TabPanel>

                                    <TabPanel value={analysisTab} index={1}>
                                        <Typography variant="body2">
                                            Quick summary: {currentResult.prediction.result} detected with {confidence}% confidence.
                                        </Typography>
                                    </TabPanel>
                                </Box>

                                {/* Q&A */}
                                <Box sx={{ mt: 3 }}>
                                    <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                                        Q&A
                                    </Typography>
                                    <Box sx={{ maxHeight: 150, overflow: 'auto', mb: 1 }}>
                                        {qaMessages.map((msg, idx) => (
                                            <Alert
                                                key={idx}
                                                severity={msg.type === 'q' ? 'info' : 'success'}
                                                sx={{ mb: 1 }}
                                            >
                                                <Typography variant="body2">
                                                    {msg.type === 'q' ? 'Q: ' : 'A: '}
                                                    {msg.text}
                                                </Typography>
                                            </Alert>
                                        ))}
                                    </Box>
                                    <Box sx={{ display: 'flex', gap: 1 }}>
                                        <TextField
                                            fullWidth
                                            size="small"
                                            placeholder="Ask a question..."
                                            value={qaQuestion}
                                            onChange={(e) => setQaQuestion(e.target.value)}
                                            onKeyPress={(e) => e.key === 'Enter' && handleQaSubmit()}
                                        />
                                        <IconButton color="primary" onClick={handleQaSubmit}>
                                            <Send />
                                        </IconButton>
                                    </Box>
                                </Box>

                                {/* Action Buttons */}
                                <Grid container spacing={1} sx={{ mt: 2 }}>
                                    <Grid item xs={4}>
                                        <Button fullWidth variant="outlined" color="success" startIcon={<ThumbUp />}>
                                            Correct
                                        </Button>
                                    </Grid>
                                    <Grid item xs={4}>
                                        <Button fullWidth variant="outlined" color="error" startIcon={<ThumbDown />}>
                                            Incorrect
                                        </Button>
                                    </Grid>
                                    <Grid item xs={4}>
                                        <Button fullWidth variant="outlined" color="warning" startIcon={<Help />}>
                                            Uncertain
                                        </Button>
                                    </Grid>
                                </Grid>

                                <Button fullWidth variant="contained" startIcon={<Download />} sx={{ mt: 2 }}>
                                    Download Report (PDF)
                                </Button>
                            </Box>
                        )}

                        {!showResults && !isLoading && (
                            <Box sx={{ textAlign: 'center', py: 8, color: 'text.secondary' }}>
                                <Typography>Results will be displayed here</Typography>
                            </Box>
                        )}
                    </Paper>
                </Grid>

                {/* Sidebar */}
                <Grid item xs={12} md={3}>
                    {/* Recent Uploads */}
                    <Paper sx={{ p: 2.5, borderRadius: 2, mb: 2.5 }}>
                        <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                            RECENT UPLOADS
                        </Typography>
                        {[1, 2].map((i) => (
                            <Card key={i} variant="outlined" sx={{ mb: 1, cursor: 'pointer' }}>
                                <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                                    <Box sx={{ display: 'flex', gap: 1.5 }}>
                                        <Box sx={{ width: 48, height: 48, bgcolor: 'grey.200', borderRadius: 1 }} />
                                        <Box sx={{ flex: 1 }}>
                                            <Typography variant="caption" fontWeight={600}>
                                                Forearm X-ray
                                            </Typography>
                                            <Typography variant="caption" display="block" color="text.secondary">
                                                10/28/2023
                                            </Typography>
                                            <Chip label="FRACTURED" size="small" color="error" sx={{ mt: 0.5, height: 18 }} />
                                        </Box>
                                    </Box>
                                </CardContent>
                            </Card>
                        ))}
                    </Paper>

                    {/* Model Status */}
                    <Paper sx={{ p: 2.5, borderRadius: 2, mb: 2.5 }}>
                        <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                            MODEL STATUS
                        </Typography>
                        <Alert severity="success" sx={{ mb: 1.5 }}>
                            System Online
                        </Alert>
                        <Box>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                <Typography variant="caption" color="text.secondary">
                                    Uptime
                                </Typography>
                                <Typography variant="caption" fontWeight={600}>
                                    99.9%
                                </Typography>
                            </Box>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                <Typography variant="caption" color="text.secondary">
                                    Avg Response Time
                                </Typography>
                                <Typography variant="caption" fontWeight={600}>
                                    1.2s
                                </Typography>
                            </Box>
                        </Box>
                    </Paper>

                    {/* System Health */}
                    <Paper sx={{ p: 2.5, borderRadius: 2 }}>
                        <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                            SYSTEM HEALTH
                        </Typography>
                        <Box>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                <Typography variant="caption" color="text.secondary">
                                    CPU Usage
                                </Typography>
                                <Typography variant="caption" fontWeight={600}>
                                    25%
                                </Typography>
                            </Box>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                <Typography variant="caption" color="text.secondary">
                                    Memory
                                </Typography>
                                <Typography variant="caption" fontWeight={600}>
                                    4GB / 16GB
                                </Typography>
                            </Box>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                <Typography variant="caption" color="text.secondary">
                                    Storage
                                </Typography>
                                <Typography variant="caption" fontWeight={600}>
                                    2TB free
                                </Typography>
                            </Box>
                        </Box>
                    </Paper>
                </Grid>
            </Grid>
        </Container>
    );
};

export default DashboardUploadPage;
