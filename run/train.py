import argparse, time, os
import model

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--train-filename", "-file", type=str, default=None, help="訓練用のテキストファイルのパス")
	parser.add_argument("--train-directory", "-dir", type=str, default=None, help="訓練用のテキストファイルが入っているディレクトリ")
	parser.add_argument("--seed", type=int, default=1)
	parser.add_argument("--epochs", "-e", type=int, default=100000, help="総epoch")
	parser.add_argument("--working-directory", "-cwd", type=str, default="out", help="ワーキングディレクトリ")
	parser.add_argument("--train-split", "-split", type=float, default=0.9, help="テキストデータの何割を訓練データにするか")
	parser.add_argument("--lambda-a", "-lam-a", type=float, default=4)
	parser.add_argument("--lambda-b", "-lam-b", type=float, default=1)
	parser.add_argument("--vpylm-beta-stop", "-beta-stop", type=float, default=4)
	parser.add_argument("--vpylm-beta-pass", "-beta-pass", type=float, default=1)
	parser.add_argument("--max-word-length", "-l", type=int, default=16, help="可能な単語の最大長.")
	args = parser.parse_args()

	assert args.working_directory is not None
	try:
		os.mkdir(args.working_directory)
	except:
		pass

		

	trainer = model.trainer()

	# テキストファイルの追加
	if args.input_dir is not None:
		assert os.path.exists(args.input_dir)
		files = os.listdir(args.input_dir)
		for filename in files:
			if filename.endswith(".txt"):
				print "loading", filename
				trainer.add_textfile(args.input_dir + "/" + filename, args.train_split)
	elif args.input_filename is not None:
		assert os.path.exists(args.input_filename)
		print "loading", args.input_filename
		trainer.add_textfile(args.input_filename, args.train_split)
	else:
		raise Exception()

	# ハイパーパラメータの設定
	trainer.set_lambda_prior(4, 1)		# lambdaの事前分布（ガンマ分布）のハイパーパラメータ

	# NPYLMでは通常、新しい分割結果をもとに単語nグラムモデルを更新する
	# Falseを渡すと分割結果の単語列としての確率が以前の分割のそれよりも下回っている場合に確率的に棄却する
	# Falseの方が切りすぎない分割結果になるが切りすぎなさすぎることもある
	trainer.set_always_accept_new_segmentation(True)

	# 可能な単語の最大長を指定
	trainer.set_max_word_length(args.max_word_length)

	# 必要なメモリを確保
	# データを追加し終わってから呼ぶ
	trainer.compile()

	# 文字列の単語IDが衝突しているかどうかをチェック
	# 時間の無駄なので一度したらしなくてよい
	# メモリを大量に消費します
	if False:
		print "ハッシュの衝突を確認中 ..."
		num_checked_words = trainer.detect_collision()
		print "\r\033[2K衝突はありません", "({} 単語)".format(num_checked_words)

	max_epoch = 500
	num_sentences_train = trainer.get_num_sentences_train()
	num_sentences_test = trainer.get_num_sentences_test()
	print "データ:"
	print "	{}	(学習)".format(num_sentences_train)
	print "	{}	(テスト)".format(num_sentences_test)
	total_time = 0
	for epoch in xrange(1, max_epoch):
		start_time = time.time()

		# ギブスサンプリング
		trainer.perform_gibbs_sampling()

		# ハイパーパラメータの推定
		trainer.sample_pitman_yor_hyperparameters()
		trainer.sample_lambda()

		if epoch > 3:
			trainer.update_Pk_vpylm()

		elapsed_time = time.time() - start_time
		total_time += elapsed_time
		ppl = trainer.compute_perplexity_test()
		print "\r\033[2KEpoch {} / {} - {} min - {} sentences/sec - {} ppl - {} min total".format(
			epoch,
			max_epoch,
			int(elapsed_time / 60),
			int(num_sentences_train / elapsed_time),
			ppl,
			int(total_time / 60)
		)
		if epoch > 1:
			# 客数などの表示
			trainer.dump_hpylm()
			trainer.dump_vpylm()
			# VPYLMから長さkの単語が出現する確率を表示
			trainer.dump_Pk_vpylm()
			# 文字種ごとのλ
			trainer.dump_lambda()
			# Forward filtering-Backward samplingによる分割を表示
			print "forward-backward:"
			trainer.show_sampled_segmentation_train(5)
			print "forward-backward:"
			trainer.show_sampled_segmentation_test(5)
			# ビタビアルゴリズムによる分割を表示
			print "viterbi:"
			trainer.show_viterbi_segmentation_train(5)
			print "viterbi:"
			trainer.show_viterbi_segmentation_test(5)
		# 保存
		trainer.save(args.model_filename)

if __name__ == "__main__":
	main()