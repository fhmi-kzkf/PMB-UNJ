"""
Unit tests untuk fungsi scoring dan ranking.
"""

from decimal import Decimal
from django.test import TestCase
from pendaftaran.services.scoring import (
    hitung_skor, ranking_pendaftar, generate_no_registrasi
)


class ScoringTestCase(TestCase):
    
    def test_hitung_skor_normal(self):
        """Test perhitungan skor dengan nilai normal."""
        # 80 * 0.6 + 90 * 0.4 = 48 + 36 = 84
        self.assertEqual(hitung_skor(80, 90), Decimal('84.00'))
        
    def test_hitung_skor_maksimal(self):
        """Test perhitungan dengan nilai sempurna."""
        self.assertEqual(hitung_skor(100, 100), Decimal('100.00'))
        
    def test_hitung_skor_nol(self):
        """Test perhitungan dengan nilai nol."""
        self.assertEqual(hitung_skor(0, 0), Decimal('0.00'))
        
    def test_hitung_skor_desimal(self):
        """Test perhitungan dengan nilai desimal."""
        # 85.5 * 0.6 + 78.5 * 0.4 = 51.3 + 31.4 = 82.70
        self.assertEqual(hitung_skor(85.5, 78.5), Decimal('82.70'))
        
    def test_hitung_skor_out_of_range(self):
        """Test validasi nilai di luar range 0-100."""
        with self.assertRaises(ValueError):
            hitung_skor(101, 90)
        with self.assertRaises(ValueError):
            hitung_skor(80, -5)


class RankingTestCase(TestCase):
    
    def setUp(self):
        self.data = [
            {'id': 1, 'nama': 'Andi', 'skor_akhir': 85.5, 'nilai_akademik': 80},
            {'id': 2, 'nama': 'Budi', 'skor_akhir': 90.0, 'nilai_akademik': 85},
            {'id': 3, 'nama': 'Cici', 'skor_akhir': 75.0, 'nilai_akademik': 70},
            {'id': 4, 'nama': 'Deni', 'skor_akhir': 85.5, 'nilai_akademik': 85}, # Tie dengan Andi, akademik lebih tinggi
            {'id': 5, 'nama': 'Eka', 'skor_akhir': 60.0, 'nilai_akademik': 60},
        ]
        
    def test_ranking_sorting_and_status(self):
        """Test pengurutan dan penetapan status kelulusan."""
        # Kuota: 2 lulus, 1 cadangan
        hasil = ranking_pendaftar(self.data, kuota=2, kuota_cadangan=1)
        
        # Urutan yang diharapkan: Budi (90), Deni (85.5, 85), Andi (85.5, 80), Cici (75), Eka (60)
        self.assertEqual(hasil[0]['nama'], 'Budi')
        self.assertEqual(hasil[0]['status_seleksi'], 'lulus')
        self.assertEqual(hasil[0]['ranking'], 1)
        
        self.assertEqual(hasil[1]['nama'], 'Deni')
        self.assertEqual(hasil[1]['status_seleksi'], 'lulus')
        self.assertEqual(hasil[1]['ranking'], 2)
        
        self.assertEqual(hasil[2]['nama'], 'Andi')
        self.assertEqual(hasil[2]['status_seleksi'], 'cadangan')
        self.assertEqual(hasil[2]['ranking'], 3)
        
        self.assertEqual(hasil[3]['nama'], 'Cici')
        self.assertEqual(hasil[3]['status_seleksi'], 'tidak_lulus')
        
        self.assertEqual(hasil[4]['nama'], 'Eka')
        self.assertEqual(hasil[4]['status_seleksi'], 'tidak_lulus')

    def test_generate_no_registrasi(self):
        """Test format nomor registrasi."""
        no_reg = generate_no_registrasi()
        self.assertTrue(no_reg.startswith('PMB-'))
        self.assertEqual(len(no_reg.split('-')), 3)
