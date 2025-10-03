#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OnlyVips Issue Senkronizasyon Betiği

Bu betik, markdown dosyalarındaki TODO maddelerini GitHub issue'larına dönüştürür.
Issue config dosyasında tanımlanan kalıpları kullanarak ilgili görevleri bulur ve GitHub'a senkronize eder.
"""

import os
import re
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Set

import requests
from github import Github
from github.Issue import Issue
from github.GithubException import GithubException
from tqdm import tqdm
from colorama import Fore, Style, init

# Colorama başlatma
init(autoreset=True)

# Loglama yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("sync_issues.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("issue_sync")

CONFIG_FILE = '.github/issue_config.json'
DEFAULT_REPO = os.environ.get('GITHUB_REPOSITORY')
DEFAULT_TOKEN = os.environ.get('GH_TOKEN')
DEFAULT_BRANCH = 'main'

class IssueSync:
    """GitHub issue senkronizasyon işleyici sınıfı"""
    
    def __init__(self, config_file: str, repo_name: str, token: str, branch: str = DEFAULT_BRANCH) -> None:
        """
        Issue senkronizasyon işleyicisini başlatır
        
        Args:
            config_file: Yapılandırma dosyası yolu
            repo_name: GitHub repo adı (kullanıcı/repo formatında)
            token: GitHub API token'ı
            branch: Kontrol edilecek dal (varsayılan: main)
        """
        self.config_file = config_file
        self.repo_name = repo_name
        self.branch = branch
        self.gh = Github(token)
        self.repo = self.gh.get_repo(repo_name)
        
        # Yapılandırma yükleme
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Yapılandırma dosyası yüklenemedi: {str(e)}")
            raise
        
        self.patterns = self.config.get("issue_patterns", [])
        self.file_patterns = self.config.get("file_patterns", {})
        self.ignore_patterns = self.config.get("ignore_patterns", [])
        
        # GitHub'daki mevcut issue'ları getir
        self.existing_issues = self._get_existing_issues()
        self.processed_issues = set()
        
        logger.info(f"GitHub issue senkronizasyonu başlatıldı: {repo_name}, dal: {branch}")
        logger.info(f"{len(self.existing_issues)} mevcut issue bulundu")
    
    def _get_existing_issues(self) -> Dict[str, Issue]:
        """
        Repository'deki mevcut tüm açık issue'ları getirir
        
        Returns:
            Dict[str, Issue]: Başlığa göre issue sözlüğü
        """
        issues = {}
        
        try:
            for issue in self.repo.get_issues(state="open"):
                # Sadece bu script tarafından oluşturulan issue'ları dikkate al
                # Issue başlığının başında [README], [ROADMAP] vb. etiketleri arar
                if re.match(r"^\[\w+\]", issue.title):
                    issues[issue.title] = issue
        except GithubException as e:
            logger.error(f"GitHub issue'ları getirirken hata: {str(e)}")
        
        return issues
    
    def _create_label(self, label_info: Dict[str, str]) -> None:
        """
        GitHub'da bir etiket oluşturur veya günceller
        
        Args:
            label_info: Etiket bilgileri {"name": str, "color": str, "description": str}
        """
        name = label_info["name"]
        color = label_info["color"]
        description = label_info.get("description", "")
        
        try:
            try:
                label = self.repo.get_label(name)
                # Etiket varsa güncelle
                label.edit(name=name, color=color, description=description)
            except GithubException:
                # Etiket yoksa oluştur
                self.repo.create_label(name=name, color=color, description=description)
                logger.info(f"Yeni etiket oluşturuldu: {name}")
        except GithubException as e:
            logger.error(f"Etiket oluştururken/güncellerken hata: {str(e)}")
    
    def setup_labels(self) -> None:
        """Yapılandırma dosyasında tanımlanan etiketleri oluşturur"""
        labels = self.config.get("labels", [])
        logger.info(f"{len(labels)} etiket yapılandırılıyor...")
        
        for label_info in labels:
            self._create_label(label_info)
    
    def _process_file(self, file_path: str, file_type: str) -> List[Dict[str, Any]]:
        """
        Belirli dosya tipine göre görevleri işler
        
        Args:
            file_path: İşlenecek dosya yolu
            file_type: Dosya tipi (README.md, ROADMAP.MD, TODO.md vb.)
            
        Returns:
            List[Dict[str, Any]]: İşlenen görevlerin listesi
        """
        issues = []
        file_config = self.file_patterns.get(file_type, {})
        process_entire_file = file_config.get("process_entire_file", False)
        section_patterns = file_config.get("section_patterns", [])
        
        try:
            try:
                file_content = self.repo.get_contents(file_path, ref=self.branch).decoded_content.decode('utf-8')
            except UnicodeDecodeError:
                # UTF-8 dekodasyon hatası durumunda ISO-8859-1 dene
                file_content = self.repo.get_contents(file_path, ref=self.branch).decoded_content.decode('iso-8859-1')
        except GithubException as e:
            logger.error(f"Dosya içeriği alınırken hata: {file_path}, {str(e)}")
            return issues
        
        lines = file_content.split("\n")
        in_section = process_entire_file  # Tüm dosyayı işle seçeneği varsa baştan true
        
        for i, line in enumerate(lines):
            # Bölüm başlıklarını kontrol et
            if not process_entire_file and section_patterns:
                for pattern in section_patterns:
                    if re.match(pattern, line):
                        in_section = True
                        break
                if not in_section and line.startswith("#"):
                    in_section = False
            
            if in_section:
                # Her kalıp için kontrol et
                for pattern_config in self.patterns:
                    pattern = pattern_config["pattern"]
                    match = re.search(pattern, line)
                    
                    if match:
                        # İşlenecek görevleri atla
                        skip = False
                        for ignore_pattern in self.ignore_patterns:
                            if re.search(ignore_pattern, line):
                                skip = True
                                break
                        
                        if skip:
                            continue
                        
                        task_desc = match.group(1).strip()
                        task_type = match.group(2) if match.groups() and len(match.groups()) > 1 else None
                        task_priority = match.group(3) if match.groups() and len(match.groups()) > 2 else None
                        
                        # Etiketleri belirle
                        label_mapping = pattern_config.get("label_mapping", {})
                        default_label = pattern_config.get("default_label", "task")
                        
                        labels = []
                        if task_type and task_type in label_mapping:
                            labels.append(label_mapping[task_type])
                        else:
                            labels.append(default_label)
                        
                        if task_priority:
                            labels.append(f"priority:{task_priority}")
                        
                        # Issue başlığı
                        title = f"[{os.path.basename(file_path)}] {task_desc}"
                        
                        # Bağlam bilgisi
                        context_start = max(0, i - 3)
                        context_end = min(len(lines), i + 3)
                        context_lines = lines[context_start:context_end]
                        context = "\n".join(context_lines)
                        
                        issue_data = {
                            "title": title,
                            "body": f"## Görev\n\n{task_desc}\n\n## Kaynak\n\n`{file_path}` dosyasının {i+1}. satırından oluşturuldu.\n\n## Bağlam\n\n```markdown\n{context}\n```",
                            "labels": labels,
                            "line": i+1,
                            "file_path": file_path
                        }
                        
                        issues.append(issue_data)
                        break  # Aynı satırı başka bir kalıpla tekrar kontrol etme
        
        return issues
    
    def process_files(self) -> List[Dict[str, Any]]:
        """
        Belirtilen dosya tiplerini işler ve görevleri çıkarır
        
        Returns:
            List[Dict[str, Any]]: Tüm dosyalardan çıkarılan görevlerin listesi
        """
        all_issues = []
        file_types = self.file_patterns.keys()
        
        # Repo'daki markdown dosyalarını bul
        try:
            contents = self.repo.get_contents("", ref=self.branch)
            files_to_process = []
            
            # Tüm dosyaları toplayalım (recursive olarak)
            while contents:
                file_content = contents.pop(0)
                if file_content.type == "dir":
                    contents.extend(self.repo.get_contents(file_content.path, ref=self.branch))
                else:
                    file_name = os.path.basename(file_content.path)
                    if file_name in file_types:
                        files_to_process.append((file_content.path, file_name))
        except GithubException as e:
            logger.error(f"Repo içeriği alınırken hata: {str(e)}")
            return all_issues
        
        logger.info(f"{len(files_to_process)} dosya işlenecek")
        
        # Her dosyayı işle
        for file_path, file_type in tqdm(files_to_process):
            logger.info(f"İşleniyor: {file_path}")
            issues = self._process_file(file_path, file_type)
            all_issues.extend(issues)
            logger.info(f"{file_path} dosyasında {len(issues)} görev bulundu")
        
        return all_issues
    
    def create_or_update_issues(self, issues: List[Dict[str, Any]]) -> Tuple[int, int, int]:
        """
        Bulunan görevler için GitHub issue'ları oluşturur veya günceller
        
        Args:
            issues: Oluşturulacak issue'ların listesi
            
        Returns:
            Tuple[int, int, int]: Oluşturulan, güncellenen ve atlanan issue sayıları
        """
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for issue_data in tqdm(issues):
            title = issue_data["title"]
            body = issue_data["body"]
            labels = issue_data["labels"]
            
            if title in self.existing_issues:
                # Issue zaten var, güncelle
                existing_issue = self.existing_issues[title]
                try:
                    existing_issue.edit(body=body, labels=labels)
                    logger.info(f"Issue güncellendi: {title}")
                    updated_count += 1
                except GithubException as e:
                    logger.error(f"Issue güncellenirken hata: {title}, {str(e)}")
            else:
                # Yeni issue oluştur
                try:
                    self.repo.create_issue(title=title, body=body, labels=labels)
                    logger.info(f"Yeni issue oluşturuldu: {title}")
                    created_count += 1
                except GithubException as e:
                    logger.error(f"Issue oluşturulurken hata: {title}, {str(e)}")
            
            self.processed_issues.add(title)
        
        return created_count, updated_count, skipped_count
    
    def close_removed_issues(self) -> int:
        """
        Markdown dosyalarından kaldırılan görevlerin issue'larını kapatır
        
        Returns:
            int: Kapatılan issue sayısı
        """
        closed_count = 0
        
        for title, issue in self.existing_issues.items():
            if title not in self.processed_issues:
                try:
                    issue.edit(state="closed")
                    issue.create_comment("Bu görev kaynak dosyalardan kaldırıldığı için otomatik olarak kapatılmıştır.")
                    logger.info(f"Issue kapatıldı: {title}")
                    closed_count += 1
                except GithubException as e:
                    logger.error(f"Issue kapatılırken hata: {title}, {str(e)}")
        
        return closed_count
    
    def run(self) -> Tuple[int, int, int, int]:
        """
        Tüm senkronizasyon işlemini yürütür
        
        Returns:
            Tuple[int, int, int, int]: Oluşturulan, güncellenen, atlanan ve kapatılan issue sayıları
        """
        # Etiketleri hazırla
        self.setup_labels()
        
        # Dosyaları işle ve görevleri çıkar
        issues = self.process_files()
        logger.info(f"Toplam {len(issues)} görev bulundu")
        
        # Issue'ları oluştur veya güncelle
        created, updated, skipped = self.create_or_update_issues(issues)
        
        # Kaldırılan görevlerin issue'larını kapat
        closed = self.close_removed_issues()
        
        return created, updated, skipped, closed

def main() -> None:
    """Ana işlev"""
    
    parser = argparse.ArgumentParser(description="Markdown dosyalarındaki görevleri GitHub issue'larına senkronize eder")
    parser.add_argument('--config', default=CONFIG_FILE, help='Yapılandırma dosyası yolu')
    parser.add_argument('--repo', default=DEFAULT_REPO, help='GitHub repo adı (kullanıcı/repo formatında)')
    parser.add_argument('--token', default=DEFAULT_TOKEN, help='GitHub API token')
    parser.add_argument('--branch', default=DEFAULT_BRANCH, help='Kontrol edilecek dal')
    args = parser.parse_args()
    
    if not args.token:
        logger.error("GitHub token sağlanmadı. GH_TOKEN ortam değişkenini ayarlayın veya --token parametresini kullanın.")
        return
    
    if not args.repo:
        logger.error("GitHub repo adı sağlanmadı. GITHUB_REPOSITORY ortam değişkenini ayarlayın veya --repo parametresini kullanın.")
        return
    
    try:
        # Issue senkronizasyon işleyicisini başlat
        issue_sync = IssueSync(
            config_file=args.config,
            repo_name=args.repo,
            token=args.token,
            branch=args.branch
        )
        
        # İşlemi yürüt
        created, updated, skipped, closed = issue_sync.run()
        
        # Sonuçları raporla
        logger.info(f"{Fore.GREEN}İşlem tamamlandı!{Style.RESET_ALL}")
        logger.info(f"{Fore.GREEN}{created} yeni issue oluşturuldu.{Style.RESET_ALL}")
        logger.info(f"{Fore.YELLOW}{updated} issue güncellendi.{Style.RESET_ALL}")
        logger.info(f"{Fore.CYAN}{skipped} issue atlandı.{Style.RESET_ALL}")
        logger.info(f"{Fore.RED}{closed} issue kapatıldı.{Style.RESET_ALL}")
        
    except Exception as e:
        logger.error(f"İşlem sırasında hata: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main() 