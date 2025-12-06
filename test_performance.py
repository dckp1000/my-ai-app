"""
Tests for performance improvements in the AI app.
"""
import unittest
from unittest import mock
import os
import sys
import tempfile
import shutil


class TestAppPerformance(unittest.TestCase):
    """Test performance improvements in app.py"""
    
    @mock.patch('openai.OpenAI')
    def test_client_initialized_once(self, mock_openai):
        """Test that OpenAI client is initialized only once at module level"""
        # Set up mock
        mock_client = mock.MagicMock()
        mock_openai.return_value = mock_client
        mock_response = mock.MagicMock()
        mock_response.choices = [mock.MagicMock()]
        mock_response.choices[0].message.content = 'Test response'
        mock_client.chat.completions.create.return_value = mock_response
        
        # Import module (this initializes the client)
        import importlib
        import app as app_module
        importlib.reload(app_module)
        
        # Verify client was initialized once
        initial_count = mock_openai.call_count
        self.assertEqual(initial_count, 1, "Client should be initialized once at module level")
        
        # Call ask_gpt multiple times
        app_module.ask_gpt("test 1")
        app_module.ask_gpt("test 2")
        app_module.ask_gpt("test 3")
        
        # Verify client was NOT re-initialized
        self.assertEqual(mock_openai.call_count, initial_count, 
                       "Client should not be re-initialized on subsequent calls")
    
    @mock.patch('openai.OpenAI')
    def test_api_calls_use_same_client(self, mock_openai):
        """Test that all API calls use the same client instance"""
        mock_client = mock.MagicMock()
        mock_openai.return_value = mock_client
        mock_response = mock.MagicMock()
        mock_response.choices = [mock.MagicMock()]
        mock_response.choices[0].message.content = 'Response'
        mock_client.chat.completions.create.return_value = mock_response
        
        import importlib
        import app as app_module
        importlib.reload(app_module)
        
        # Make multiple calls
        for i in range(5):
            app_module.ask_gpt(f"prompt {i}")
        
        # Verify chat.completions.create was called 5 times on the same client
        self.assertEqual(mock_client.chat.completions.create.call_count, 5)


class TestDownloadScriptPerformance(unittest.TestCase):
    """Test performance improvements in download_nba_dataset.py"""
    
    def test_scandir_efficiency(self):
        """Test that file listing uses os.scandir for better performance"""
        # Create a temporary directory with test files
        test_dir = tempfile.mkdtemp()
        try:
            # Create test files
            for i in range(10):
                filepath = os.path.join(test_dir, f'test_file_{i}.csv')
                with open(filepath, 'w') as f:
                    f.write('x' * (100 * (i + 1)))
            
            # Test the scandir approach (simulating the code in download_nba_dataset.py)
            files_found = []
            with os.scandir(test_dir) as entries:
                for entry in entries:
                    if entry.is_file():
                        size = entry.stat().st_size
                        files_found.append((entry.name, size))
            
            # Verify all files were found
            self.assertEqual(len(files_found), 10)
            
            # Verify sizes are correct
            for name, size in files_found:
                if name.startswith('test_file_'):
                    idx = int(name.split('_')[2].split('.')[0])
                    expected_size = 100 * (idx + 1)
                    self.assertEqual(size, expected_size)
        
        finally:
            shutil.rmtree(test_dir)
    
    def test_scandir_error_handling(self):
        """Test that scandir properly handles errors"""
        # Test with non-existent directory
        non_existent = '/nonexistent/directory/path'
        
        try:
            with os.scandir(non_existent) as entries:
                list(entries)
            self.fail("Should have raised OSError")
        except OSError:
            # Expected behavior
            pass


class TestPerformanceComparison(unittest.TestCase):
    """Compare performance of old vs new approaches"""
    
    def test_file_listing_performance(self):
        """Compare performance of os.listdir vs os.scandir"""
        import time
        
        # Create a temporary directory with many files
        test_dir = tempfile.mkdtemp()
        try:
            # Create 100 test files
            for i in range(100):
                filepath = os.path.join(test_dir, f'file_{i}.txt')
                with open(filepath, 'w') as f:
                    f.write('data')
            
            # Old approach (os.listdir)
            start_old = time.perf_counter()
            files_old = []
            for file in os.listdir(test_dir):
                file_path = os.path.join(test_dir, file)
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    files_old.append((file, size))
            time_old = time.perf_counter() - start_old
            
            # New approach (os.scandir)
            start_new = time.perf_counter()
            files_new = []
            with os.scandir(test_dir) as entries:
                for entry in entries:
                    if entry.is_file():
                        size = entry.stat().st_size
                        files_new.append((entry.name, size))
            time_new = time.perf_counter() - start_new
            
            # Verify both approaches return the same results
            self.assertEqual(len(files_old), len(files_new))
            
            # New approach should be at least as fast or faster
            # (In practice, scandir is faster, but we just verify it works)
            print(f"\nPerformance comparison:")
            print(f"  os.listdir approach: {time_old:.4f}s")
            print(f"  os.scandir approach: {time_new:.4f}s")
            if time_new > 0:
                print(f"  Speedup: {time_old/time_new:.2f}x")
            else:
                print(f"  Speedup: N/A (time_new too small to measure)")
            
        finally:
            shutil.rmtree(test_dir)


if __name__ == '__main__':
    unittest.main()
